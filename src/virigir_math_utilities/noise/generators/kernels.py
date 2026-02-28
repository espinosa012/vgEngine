"""
FastNoiseLite-compatible 2D noise generation kernels using Numba JIT.

All algorithms are ported from FastNoiseLite.h to match its output exactly,
including the prime-based hash function, gradient tables, and fractal formulas.

Noise type integer codes (match FastNoiseLite enum):
    0 = OpenSimplex2
    1 = OpenSimplex2S
    2 = Cellular
    3 = Perlin
    4 = ValueCubic
    5 = Value

Fractal type integer codes:
    0 = None
    1 = FBM
    2 = Ridged
    3 = PingPong

Cellular distance function codes:
    0 = Euclidean, 1 = EuclideanSq, 2 = Manhattan, 3 = Hybrid

Cellular return type codes:
    0 = CellValue, 1 = Distance, 2 = Distance2,
    3 = Distance2Add, 4 = Distance2Sub, 5 = Distance2Mul, 6 = Distance2Div
"""

import numpy as np
from numba import njit, prange
import numba as nb
from numpy.typing import NDArray

# ============================================================================
# Integer primes (int32) for coordinate hashing
# ============================================================================
_PRIME_X = np.int32(501125321)
_PRIME_Y = np.int32(1136930381)
_HASH_MUL = np.int32(665099693)  # 0x27d4eb2d

# Simplex skew constants for 2D
_SQRT3 = 1.7320508075688772935274463415059
_F2 = np.float64(0.5 * (_SQRT3 - 1.0))   # ~0.36602540378
_G2 = np.float64((3.0 - _SQRT3) / 6.0)   # ~0.21132486540

# ============================================================================
# Lookup tables from FastNoiseLite.h
# Gradients2D: 128 unit-circle gradient pairs = 256 floats
# Indexed: h = (hash ^ hash>>15) & 254;  xg = table[h];  yg = table[h|1]
# ============================================================================
_GRADIENTS_2D = np.array([
    0.130526192220052, 0.99144486137381, 0.38268343236509, 0.923879532511287,
    0.608761429008721, 0.793353340291235, 0.793353340291235, 0.608761429008721,
    0.923879532511287, 0.38268343236509, 0.99144486137381, 0.130526192220051,
    0.99144486137381, -0.130526192220051, 0.923879532511287, -0.38268343236509,
    0.793353340291235, -0.60876142900872, 0.608761429008721, -0.793353340291235,
    0.38268343236509, -0.923879532511287, 0.130526192220052, -0.99144486137381,
    -0.130526192220052, -0.99144486137381, -0.38268343236509, -0.923879532511287,
    -0.608761429008721, -0.793353340291235, -0.793353340291235, -0.608761429008721,
    -0.923879532511287, -0.38268343236509, -0.99144486137381, -0.130526192220052,
    -0.99144486137381, 0.130526192220051, -0.923879532511287, 0.38268343236509,
    -0.793353340291235, 0.608761429008721, -0.608761429008721, 0.793353340291235,
    -0.38268343236509, 0.923879532511287, -0.130526192220052, 0.99144486137381,
    0.130526192220052, 0.99144486137381, 0.38268343236509, 0.923879532511287,
    0.608761429008721, 0.793353340291235, 0.793353340291235, 0.608761429008721,
    0.923879532511287, 0.38268343236509, 0.99144486137381, 0.130526192220051,
    0.99144486137381, -0.130526192220051, 0.923879532511287, -0.38268343236509,
    0.793353340291235, -0.60876142900872, 0.608761429008721, -0.793353340291235,
    0.38268343236509, -0.923879532511287, 0.130526192220052, -0.99144486137381,
    -0.130526192220052, -0.99144486137381, -0.38268343236509, -0.923879532511287,
    -0.608761429008721, -0.793353340291235, -0.793353340291235, -0.608761429008721,
    -0.923879532511287, -0.38268343236509, -0.99144486137381, -0.130526192220052,
    -0.99144486137381, 0.130526192220051, -0.923879532511287, 0.38268343236509,
    -0.793353340291235, 0.608761429008721, -0.608761429008721, 0.793353340291235,
    -0.38268343236509, 0.923879532511287, -0.130526192220052, 0.99144486137381,
    0.130526192220052, 0.99144486137381, 0.38268343236509, 0.923879532511287,
    0.608761429008721, 0.793353340291235, 0.793353340291235, 0.608761429008721,
    0.923879532511287, 0.38268343236509, 0.99144486137381, 0.130526192220051,
    0.99144486137381, -0.130526192220051, 0.923879532511287, -0.38268343236509,
    0.793353340291235, -0.60876142900872, 0.608761429008721, -0.793353340291235,
    0.38268343236509, -0.923879532511287, 0.130526192220052, -0.99144486137381,
    -0.130526192220052, -0.99144486137381, -0.38268343236509, -0.923879532511287,
    -0.608761429008721, -0.793353340291235, -0.793353340291235, -0.608761429008721,
    -0.923879532511287, -0.38268343236509, -0.99144486137381, -0.130526192220052,
    -0.99144486137381, 0.130526192220051, -0.923879532511287, 0.38268343236509,
    -0.793353340291235, 0.608761429008721, -0.608761429008721, 0.793353340291235,
    -0.38268343236509, 0.923879532511287, -0.130526192220052, 0.99144486137381,
    0.130526192220052, 0.99144486137381, 0.38268343236509, 0.923879532511287,
    0.608761429008721, 0.793353340291235, 0.793353340291235, 0.608761429008721,
    0.923879532511287, 0.38268343236509, 0.99144486137381, 0.130526192220051,
    0.99144486137381, -0.130526192220051, 0.923879532511287, -0.38268343236509,
    0.793353340291235, -0.60876142900872, 0.608761429008721, -0.793353340291235,
    0.38268343236509, -0.923879532511287, 0.130526192220052, -0.99144486137381,
    -0.130526192220052, -0.99144486137381, -0.38268343236509, -0.923879532511287,
    -0.608761429008721, -0.793353340291235, -0.793353340291235, -0.608761429008721,
    -0.923879532511287, -0.38268343236509, -0.99144486137381, -0.130526192220052,
    -0.99144486137381, 0.130526192220051, -0.923879532511287, 0.38268343236509,
    -0.793353340291235, 0.608761429008721, -0.608761429008721, 0.793353340291235,
    -0.38268343236509, 0.923879532511287, -0.130526192220052, 0.99144486137381,
    0.130526192220052, 0.99144486137381, 0.38268343236509, 0.923879532511287,
    0.608761429008721, 0.793353340291235, 0.793353340291235, 0.608761429008721,
    0.923879532511287, 0.38268343236509, 0.99144486137381, 0.130526192220051,
    0.99144486137381, -0.130526192220051, 0.923879532511287, -0.38268343236509,
    0.793353340291235, -0.60876142900872, 0.608761429008721, -0.793353340291235,
    0.38268343236509, -0.923879532511287, 0.130526192220052, -0.99144486137381,
    -0.130526192220052, -0.99144486137381, -0.38268343236509, -0.923879532511287,
    -0.608761429008721, -0.793353340291235, -0.793353340291235, -0.608761429008721,
    -0.923879532511287, -0.38268343236509, -0.99144486137381, -0.130526192220052,
    -0.99144486137381, 0.130526192220051, -0.923879532511287, 0.38268343236509,
    -0.793353340291235, 0.608761429008721, -0.608761429008721, 0.793353340291235,
    -0.38268343236509, 0.923879532511287, -0.130526192220052, 0.99144486137381,
    # Last 8 pairs (from FastNoiseLite.h lines 2494-2495)
    0.38268343236509, 0.923879532511287, 0.923879532511287, 0.38268343236509,
    0.923879532511287, -0.38268343236509, 0.38268343236509, -0.923879532511287,
    -0.38268343236509, -0.923879532511287, -0.923879532511287, -0.38268343236509,
    -0.923879532511287, 0.38268343236509, -0.38268343236509, 0.923879532511287,
], dtype=np.float32)

# RandVecs2D: 256 random unit vector pairs = 512 floats
# Indexed: h = hash & (255 << 1);  x = table[h];  y = table[h|1]
_RAND_VECS_2D = np.array([
    -0.2700222198, -0.9628540911, 0.3863092627, -0.9223693152, 0.04444859006, -0.999011673, -0.5992523158, -0.8005602176,
    -0.7819280288, 0.6233687174, 0.9464672271, 0.3227999196, -0.6514146797, -0.7587218957, 0.9378472289, 0.347048376,
    -0.8497875957, -0.5271252623, -0.879042592, 0.4767432447, -0.892300288, -0.4514423508, -0.379844434, -0.9250503802,
    -0.9951650832, 0.0982163789, 0.7724397808, -0.6350880136, 0.7573283322, -0.6530343002, -0.9928004525, -0.119780055,
    -0.0532665713, 0.9985803285, 0.9754253726, -0.2203300762, -0.7665018163, 0.6422421394, 0.991636706, 0.1290606184,
    -0.994696838, 0.1028503788, -0.5379205513, -0.84299554, 0.5022815471, -0.8647041387, 0.4559821461, -0.8899889226,
    -0.8659131224, -0.5001944266, 0.0879458407, -0.9961252577, -0.5051684983, 0.8630207346, 0.7753185226, -0.6315704146,
    -0.6921944612, 0.7217110418, -0.5191659449, -0.8546734591, 0.8978622882, -0.4402764035, -0.1706774107, 0.9853269617,
    -0.9353430106, -0.3537420705, -0.9992404798, 0.03896746794, -0.2882064021, -0.9575683108, -0.9663811329, 0.2571137995,
    -0.8759714238, -0.4823630009, -0.8303123018, -0.5572983775, 0.05110133755, -0.9986934731, -0.8558373281, -0.5172450752,
    0.09887025282, 0.9951003332, 0.9189016087, 0.3944867976, -0.2439375892, -0.9697909324, -0.8121409387, -0.5834613061,
    -0.9910431363, 0.1335421355, 0.8492423985, -0.5280031709, -0.9717838994, -0.2358729591, 0.9949457207, 0.1004142068,
    0.6241065508, -0.7813392434, 0.662910307, 0.7486988212, -0.7197418176, 0.6942418282, -0.8143370775, -0.5803922158,
    0.104521054, -0.9945226741, -0.1065926113, -0.9943027784, 0.445799684, -0.8951327509, 0.105547406, 0.9944142724,
    -0.992790267, 0.1198644477, -0.8334366408, 0.552615025, 0.9115561563, -0.4111755999, 0.8285544909, -0.5599084351,
    0.7217097654, -0.6921957921, 0.4940492677, -0.8694339084, -0.3652321272, -0.9309164803, -0.9696606758, 0.2444548501,
    0.08925509731, -0.996008799, 0.5354071276, -0.8445941083, -0.1053576186, 0.9944343981, -0.9890284586, 0.1477251101,
    0.004856104961, 0.9999882091, 0.9885598478, 0.1508291331, 0.9286129562, -0.3710498316, -0.5832393863, -0.8123003252,
    0.3015207509, 0.9534596146, -0.9575110528, 0.2883965738, 0.9715802154, -0.2367105511, 0.229981792, 0.9731949318,
    0.955763816, -0.2941352207, 0.740956116, 0.6715534485, -0.9971513787, -0.07542630764, 0.6905710663, -0.7232645452,
    -0.290713703, -0.9568100872, 0.5912777791, -0.8064679708, -0.9454592212, -0.325740481, 0.6664455681, 0.74555369,
    0.6236134912, 0.7817328275, 0.9126993851, -0.4086316587, -0.8191762011, 0.5735419353, -0.8812745759, -0.4726046147,
    0.9953313627, 0.09651672651, 0.9855650846, -0.1692969699, -0.8495980887, 0.5274306472, 0.6174853946, -0.7865823463,
    0.8508156371, 0.52546432, 0.9985032451, -0.05469249926, 0.1971371563, -0.9803759185, 0.6607855748, -0.7505747292,
    -0.03097494063, 0.9995201614, -0.6731660801, 0.739491331, -0.7195018362, -0.6944905383, 0.9727511689, 0.2318515979,
    0.9997059088, -0.0242506907, 0.4421787429, -0.8969269532, 0.9981350961, -0.061043673, -0.9173660799, -0.3980445648,
    -0.8150056635, -0.5794529907, -0.8789331304, 0.4769450202, 0.0158605829, 0.999874213, -0.8095464474, 0.5870558317,
    -0.9165898907, -0.3998286786, -0.8023542565, 0.5968480938, -0.5176737917, 0.8555780767, -0.8154407307, -0.5788405779,
    0.4022010347, -0.9155513791, -0.9052556868, -0.4248672045, 0.7317445619, 0.6815789728, -0.5647632201, -0.8252529947,
    -0.8403276335, -0.5420788397, -0.9314281527, 0.363925262, 0.5238198472, 0.8518290719, 0.7432803869, -0.6689800195,
    -0.985371561, -0.1704197369, 0.4601468731, 0.88784281, 0.825855404, 0.5638819483, 0.6182366099, 0.7859920446,
    0.8331502863, -0.553046653, 0.1500307506, 0.9886813308, -0.662330369, -0.7492119075, -0.668598664, 0.743623444,
    0.7025606278, 0.7116238924, -0.5419389763, -0.8404178401, -0.3388616456, 0.9408362159, 0.8331530315, 0.5530425174,
    -0.2989720662, -0.9542618632, 0.2638522993, 0.9645630949, 0.124108739, -0.9922686234, -0.7282649308, -0.6852956957,
    0.6962500149, 0.7177993569, -0.9183535368, 0.3957610156, -0.6326102274, -0.7744703352, -0.9331891859, -0.359385508,
    -0.1153779357, -0.9933216659, 0.9514974788, -0.3076565421, -0.08987977445, -0.9959526224, 0.6678496916, 0.7442961705,
    0.7952400393, -0.6062947138, -0.6462007402, -0.7631674805, -0.2733598753, 0.9619118351, 0.9669590226, -0.254931851,
    -0.9792894595, 0.2024651934, -0.5369502995, -0.8436138784, -0.270036471, -0.9628500944, -0.6400277131, 0.7683518247,
    -0.7854537493, -0.6189203566, 0.06005905383, -0.9981948257, -0.02455770378, 0.9996984141, -0.65983623, 0.751409442,
    -0.6253894466, -0.7803127835, -0.6210408851, -0.7837781695, 0.8348888491, 0.5504185768, -0.1592275245, 0.9872419133,
    0.8367622488, 0.5475663786, -0.8675753916, -0.4973056806, -0.2022662628, -0.9793305667, 0.9399189937, 0.3413975472,
    0.9877404807, -0.1561049093, -0.9034455656, 0.4287028224, 0.1269804218, -0.9919052235, -0.3819600854, 0.924178821,
    0.9754625894, 0.2201652486, -0.3204015856, -0.9472818081, -0.9874760884, 0.1577687387, 0.02535348474, -0.9996785487,
    0.4835130794, -0.8753371362, -0.2850799925, -0.9585037287, -0.06805516006, -0.99768156, -0.7885244045, -0.6150034663,
    0.3185392127, -0.9479096845, 0.8880043089, 0.4598351306, 0.6476921488, -0.7619021462, 0.9820241299, 0.1887554194,
    0.9357275128, -0.3527237187, -0.8894895414, 0.4569555293, 0.7922791302, 0.6101588153, 0.7483818261, 0.6632681526,
    -0.7288929755, -0.6846276581, 0.8729032783, -0.4878932944, 0.8288345784, 0.5594937369, 0.08074567077, 0.9967347374,
    0.9799148216, -0.1994165048, -0.580730673, -0.8140957471, -0.4700049791, -0.8826637636, 0.2409492979, 0.9705377045,
    0.9437816757, -0.3305694308, -0.8927998638, -0.4504535528, -0.8069622304, 0.5906030467, 0.06258973166, 0.9980393407,
    -0.9312597469, 0.3643559849, 0.5777449785, 0.8162173362, -0.3360095855, -0.941858566, 0.697932075, -0.7161639607,
    -0.002008157227, -0.9999979837, -0.1827294312, -0.9831632392, -0.6523911722, 0.7578824173, -0.4302626911, -0.9027037258,
    -0.9985126289, -0.05452091251, -0.01028102172, -0.9999471489, -0.4946071129, 0.8691166802, -0.2999350194, 0.9539596344,
    0.8165471961, 0.5772786819, 0.2697460475, 0.962931498, -0.7306287391, -0.6827749597, -0.7590952064, -0.6509796216,
    -0.907053853, 0.4210146171, -0.5104861064, -0.8598860013, 0.8613350597, 0.5080373165, 0.5007881595, -0.8655698812,
    -0.654158152, 0.7563577938, -0.8382755311, -0.545246856, 0.6940070834, 0.7199681717, 0.06950936031, 0.9975812994,
    0.1702942185, -0.9853932612, 0.2695973274, 0.9629731466, 0.5519612192, -0.8338697815, 0.225657487, -0.9742067022,
    0.4215262855, -0.9068161835, 0.4881873305, -0.8727388672, -0.3683854996, -0.9296731273, -0.9825390578, 0.1860564427,
    0.81256471, 0.5828709909, 0.3196460933, -0.9475370046, 0.9570913859, 0.2897862643, -0.6876655497, -0.7260276109,
    -0.9988770922, -0.047376731, -0.1250179027, 0.992154486, -0.8280133617, 0.560708367, 0.9324863769, -0.3612051451,
    0.6394653183, 0.7688199442, -0.01623847064, -0.9998681473, -0.9955014666, -0.09474613458, -0.81453315, 0.580117012,
    0.4037327978, -0.9148769469, 0.9944263371, 0.1054336766, -0.1624711654, 0.9867132919, -0.9949487814, -0.100383875,
    -0.6995302564, 0.7146029809, 0.5263414922, -0.85027327, -0.5395221479, 0.841971408, 0.6579370318, 0.7530729462,
    0.01426758847, -0.9998982128, -0.6734383991, 0.7392433447, 0.639412098, -0.7688642071, 0.9211571421, 0.3891908523,
    -0.146637214, -0.9891903394, -0.782318098, 0.6228791163, -0.5039610839, -0.8637263605, -0.7743120191, -0.6328039957,
], dtype=np.float32)


# ============================================================================
# Non-JIT helper for fractal bounding (called from Python)
# ============================================================================

def calc_fractal_bounding(octaves: int, gain: float) -> float:
    """Compute the normalization factor for fractal noise (matches FastNoiseLite)."""
    gain_abs = abs(gain)
    amp = gain_abs
    amp_fractal = 1.0
    for _ in range(1, octaves):
        amp_fractal += amp
        amp *= gain_abs
    return 1.0 / amp_fractal


# ============================================================================
# Core hash / value / gradient JIT helpers
# ============================================================================

@njit(fastmath=True, cache=True)
def _hash2d(seed, xp, yp):
    """FastNoiseLite 2D hash with intentional int32 overflow."""
    h = nb.int32(seed) ^ nb.int32(xp) ^ nb.int32(yp)
    h = nb.int32(h * nb.int32(665099693))  # 0x27d4eb2d
    return h


@njit(fastmath=True, cache=True)
def _val_coord(seed, xp, yp):
    """Hash coordinate to float in [-1, 1]."""
    h = _hash2d(seed, xp, yp)
    h = nb.int32(h * h)
    h = nb.int32(h ^ (h << nb.int32(19)))
    return nb.float32(h) * nb.float32(1.0 / 2147483648.0)


@njit(fastmath=True, cache=True)
def _grad_coord(seed, xp, yp, xd, yd):
    """Gradient dot product using FastNoiseLite gradient table."""
    h = _hash2d(seed, xp, yp)
    h = nb.int32(h ^ (h >> nb.int32(15)))
    hi = int(h) & 254  # 127 << 1; always even, range 0-254
    return nb.float64(xd) * nb.float64(_GRADIENTS_2D[hi]) + nb.float64(yd) * nb.float64(_GRADIENTS_2D[hi | 1])


@njit(fastmath=True, cache=True)
def _grad_coord_out(seed, xp, yp):
    """Random vector output for domain warp (uses RandVecs2D)."""
    h = _hash2d(seed, xp, yp)
    hi = int(h) & 510  # 255 << 1; always even, range 0-510
    return nb.float64(_RAND_VECS_2D[hi]), nb.float64(_RAND_VECS_2D[hi | 1])


@njit(fastmath=True, cache=True)
def _grad_coord_dual(seed, xp, yp, xd, yd):
    """GradCoordDual for domain warp: combines gradient dot with rand vec output."""
    h = _hash2d(seed, xp, yp)
    idx1 = int(h) & 254        # Gradients2D index (127 << 1)
    idx2 = (int(h) >> 7) & 510  # RandVecs2D index (255 << 1)
    xg = nb.float64(_GRADIENTS_2D[idx1])
    yg = nb.float64(_GRADIENTS_2D[idx1 | 1])
    value = nb.float64(xd) * xg + nb.float64(yd) * yg
    xo = value * nb.float64(_RAND_VECS_2D[idx2])
    yo = value * nb.float64(_RAND_VECS_2D[idx2 | 1])
    return xo, yo


# ============================================================================
# Interpolation helpers
# ============================================================================

@njit(fastmath=True, cache=True)
def _interp_hermite(t):
    return t * t * (3.0 - 2.0 * t)


@njit(fastmath=True, cache=True)
def _interp_quintic(t):
    return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)


@njit(fastmath=True, cache=True)
def _lerp(a, b, t):
    return a + t * (b - a)


@njit(fastmath=True, cache=True)
def _cubic_lerp(a, b, c, d, t):
    p = (d - c) - (a - b)
    return t * t * t * p + t * t * ((a - b) - p) + t * (c - a) + b


@njit(fastmath=True, cache=True)
def _ping_pong(t):
    t -= int(t * 0.5) * 2
    if t < 1.0:
        return t
    return 2.0 - t


# ============================================================================
# Single-octave noise functions
# All return values in approximately [-1, 1] (unnormalized, pre-fractal).
# Coordinates must be pre-transformed (frequency applied, skew for simplex).
# ============================================================================

@njit(fastmath=True, cache=True)
def _single_perlin(seed, x, y):
    """Perlin noise. Returns ~[-1, 1]."""
    x0 = int(np.floor(x))
    y0 = int(np.floor(y))
    xd0 = x - x0
    yd0 = y - y0
    xd1 = xd0 - 1.0
    yd1 = yd0 - 1.0
    xs = _interp_quintic(xd0)
    ys = _interp_quintic(yd0)
    x0p = nb.int32(x0) * nb.int32(501125321)
    y0p = nb.int32(y0) * nb.int32(1136930381)
    x1p = nb.int32(x0p + nb.int32(501125321))
    y1p = nb.int32(y0p + nb.int32(1136930381))
    xf0 = _lerp(_grad_coord(seed, x0p, y0p, xd0, yd0),
                 _grad_coord(seed, x1p, y0p, xd1, yd0), xs)
    xf1 = _lerp(_grad_coord(seed, x0p, y1p, xd0, yd1),
                 _grad_coord(seed, x1p, y1p, xd1, yd1), xs)
    return _lerp(xf0, xf1, ys) * 1.4247691104677813


@njit(fastmath=True, cache=True)
def _single_simplex(seed, x, y):
    """OpenSimplex2 noise. x,y must be pre-skewed with F2. Returns ~[-1, 1]."""
    G2 = 0.21132486540518711774542560974902  # (3 - sqrt(3)) / 6
    i = int(np.floor(x))
    j = int(np.floor(y))
    xi = x - i
    yi = y - j
    t = (xi + yi) * G2
    x0 = xi - t
    y0 = yi - t
    ip = nb.int32(i) * nb.int32(501125321)
    jp = nb.int32(j) * nb.int32(1136930381)
    n0 = 0.0
    n1 = 0.0
    n2 = 0.0
    a = 0.5 - x0 * x0 - y0 * y0
    if a > 0.0:
        n0 = (a * a) * (a * a) * _grad_coord(seed, ip, jp, x0, y0)
    c_val = (2.0 * (1.0 - 2.0 * G2) * (1.0 / G2 - 2.0)) * t + ((-2.0 * (1.0 - 2.0 * G2) * (1.0 - 2.0 * G2)) + a)
    if c_val > 0.0:
        x2 = x0 + (2.0 * G2 - 1.0)
        y2 = y0 + (2.0 * G2 - 1.0)
        n2 = (c_val * c_val) * (c_val * c_val) * _grad_coord(
            seed, nb.int32(ip + nb.int32(501125321)), nb.int32(jp + nb.int32(1136930381)), x2, y2)
    if y0 > x0:
        x1 = x0 + G2
        y1 = y0 + (G2 - 1.0)
        b = 0.5 - x1 * x1 - y1 * y1
        if b > 0.0:
            n1 = (b * b) * (b * b) * _grad_coord(
                seed, ip, nb.int32(jp + nb.int32(1136930381)), x1, y1)
    else:
        x1 = x0 + (G2 - 1.0)
        y1 = y0 + G2
        b = 0.5 - x1 * x1 - y1 * y1
        if b > 0.0:
            n1 = (b * b) * (b * b) * _grad_coord(
                seed, nb.int32(ip + nb.int32(501125321)), jp, x1, y1)
    return (n0 + n1 + n2) * 99.83685446303647


@njit(fastmath=True, cache=True)
def _single_opensimplex2s(seed, x, y):
    """OpenSimplex2S noise. x,y must be pre-skewed with F2. Returns ~[-1, 1]."""
    G2 = 0.21132486540518711774542560974902
    i = int(np.floor(x))
    j = int(np.floor(y))
    xi = x - i
    yi = y - j
    ip = nb.int32(i) * nb.int32(501125321)
    jp = nb.int32(j) * nb.int32(1136930381)
    i1 = nb.int32(ip + nb.int32(501125321))
    j1 = nb.int32(jp + nb.int32(1136930381))
    t = (xi + yi) * G2
    x0 = xi - t
    y0 = yi - t
    a0 = (2.0 / 3.0) - x0 * x0 - y0 * y0
    value = (a0 * a0) * (a0 * a0) * _grad_coord(seed, ip, jp, x0, y0)
    a1 = (2.0 * (1.0 - 2.0 * G2) * (1.0 / G2 - 2.0)) * t + ((-2.0 * (1.0 - 2.0 * G2) * (1.0 - 2.0 * G2)) + a0)
    x1 = x0 - (1.0 - 2.0 * G2)
    y1 = y0 - (1.0 - 2.0 * G2)
    value += (a1 * a1) * (a1 * a1) * _grad_coord(seed, i1, j1, x1, y1)
    xmyi = xi - yi
    if t > G2:
        if xi + xmyi > 1.0:
            x2 = x0 + (3.0 * G2 - 2.0)
            y2 = y0 + (3.0 * G2 - 1.0)
            a2 = (2.0 / 3.0) - x2 * x2 - y2 * y2
            if a2 > 0.0:
                value += (a2 * a2) * (a2 * a2) * _grad_coord(
                    seed, nb.int32(ip + nb.int32(501125321) * nb.int32(2)), j1, x2, y2)
        else:
            x2 = x0 + G2
            y2 = y0 + (G2 - 1.0)
            a2 = (2.0 / 3.0) - x2 * x2 - y2 * y2
            if a2 > 0.0:
                value += (a2 * a2) * (a2 * a2) * _grad_coord(seed, ip, j1, x2, y2)
        if yi - xmyi > 1.0:
            x3 = x0 + (3.0 * G2 - 1.0)
            y3 = y0 + (3.0 * G2 - 2.0)
            a3 = (2.0 / 3.0) - x3 * x3 - y3 * y3
            if a3 > 0.0:
                value += (a3 * a3) * (a3 * a3) * _grad_coord(
                    seed, i1, nb.int32(jp + nb.int32(1136930381) * nb.int32(2)), x3, y3)
        else:
            x3 = x0 + (G2 - 1.0)
            y3 = y0 + G2
            a3 = (2.0 / 3.0) - x3 * x3 - y3 * y3
            if a3 > 0.0:
                value += (a3 * a3) * (a3 * a3) * _grad_coord(seed, i1, jp, x3, y3)
    else:
        if xi + xmyi < 0.0:
            x2 = x0 + (1.0 - G2)
            y2 = y0 - G2
            a2 = (2.0 / 3.0) - x2 * x2 - y2 * y2
            if a2 > 0.0:
                value += (a2 * a2) * (a2 * a2) * _grad_coord(
                    seed, nb.int32(ip - nb.int32(501125321)), jp, x2, y2)
        else:
            x2 = x0 + (G2 - 1.0)
            y2 = y0 + G2
            a2 = (2.0 / 3.0) - x2 * x2 - y2 * y2
            if a2 > 0.0:
                value += (a2 * a2) * (a2 * a2) * _grad_coord(seed, i1, jp, x2, y2)
        if yi < xmyi:
            x2 = x0 - G2
            y2 = y0 - (G2 - 1.0)
            a2 = (2.0 / 3.0) - x2 * x2 - y2 * y2
            if a2 > 0.0:
                value += (a2 * a2) * (a2 * a2) * _grad_coord(
                    seed, ip, nb.int32(jp - nb.int32(1136930381)), x2, y2)
        else:
            x2 = x0 + G2
            y2 = y0 + (G2 - 1.0)
            a2 = (2.0 / 3.0) - x2 * x2 - y2 * y2
            if a2 > 0.0:
                value += (a2 * a2) * (a2 * a2) * _grad_coord(seed, ip, j1, x2, y2)
    return value * 18.24196194486065


@njit(fastmath=True, cache=True)
def _single_cellular(seed, x, y, dist_func, return_type, jitter):
    """Cellular (Worley) noise. Returns ~[-1, 1]."""
    xr = int(np.floor(x + 0.5))
    yr = int(np.floor(y + 0.5))
    distance0 = 1e10
    distance1 = 1e10
    closest_hash = nb.int32(0)
    cell_jitter = nb.float64(0.43701595) * jitter
    for xi in range(xr - 1, xr + 2):
        xp = nb.int32(xi) * nb.int32(501125321)
        for yi in range(yr - 1, yr + 2):
            yp = nb.int32(yi) * nb.int32(1136930381)
            h = _hash2d(seed, xp, yp)
            idx = int(h) & 510  # 255 << 1
            vec_x = nb.float64(xi - x) + nb.float64(_RAND_VECS_2D[idx]) * cell_jitter
            vec_y = nb.float64(yi - y) + nb.float64(_RAND_VECS_2D[idx | 1]) * cell_jitter
            if dist_func == 0:  # Euclidean
                new_dist = vec_x * vec_x + vec_y * vec_y
            elif dist_func == 1:  # EuclideanSq
                new_dist = vec_x * vec_x + vec_y * vec_y
            elif dist_func == 2:  # Manhattan
                new_dist = abs(vec_x) + abs(vec_y)
            else:  # Hybrid
                new_dist = (abs(vec_x) + abs(vec_y)) + (vec_x * vec_x + vec_y * vec_y)
            if new_dist < distance1:
                if new_dist < distance0:
                    distance1 = distance0
                    distance0 = new_dist
                    closest_hash = h
                else:
                    distance1 = new_dist
    if dist_func == 0 and return_type >= 1:  # Euclidean: take sqrt for Distance return types
        distance0 = np.sqrt(distance0)
        if return_type >= 2:
            distance1 = np.sqrt(distance1)
    if return_type == 0:   # CellValue
        return nb.float64(closest_hash) * (1.0 / 2147483648.0)
    elif return_type == 1:  # Distance
        return distance0 - 1.0
    elif return_type == 2:  # Distance2
        return distance1 - 1.0
    elif return_type == 3:  # Distance2Add
        return (distance1 + distance0) * 0.5 - 1.0
    elif return_type == 4:  # Distance2Sub
        return distance1 - distance0 - 1.0
    elif return_type == 5:  # Distance2Mul
        return distance1 * distance0 * 0.5 - 1.0
    else:                  # Distance2Div
        if distance1 != 0.0:
            return distance0 / distance1 - 1.0
        return -1.0


@njit(fastmath=True, cache=True)
def _single_value(seed, x, y):
    """Value noise. Returns [-1, 1]."""
    x0 = int(np.floor(x))
    y0 = int(np.floor(y))
    xs = _interp_hermite(x - x0)
    ys = _interp_hermite(y - y0)
    x0p = nb.int32(x0) * nb.int32(501125321)
    y0p = nb.int32(y0) * nb.int32(1136930381)
    x1p = nb.int32(x0p + nb.int32(501125321))
    y1p = nb.int32(y0p + nb.int32(1136930381))
    xf0 = _lerp(_val_coord(seed, x0p, y0p), _val_coord(seed, x1p, y0p), xs)
    xf1 = _lerp(_val_coord(seed, x0p, y1p), _val_coord(seed, x1p, y1p), xs)
    return _lerp(xf0, xf1, ys)


@njit(fastmath=True, cache=True)
def _single_value_cubic(seed, x, y):
    """ValueCubic noise. Returns ~[-1, 1]."""
    x1 = int(np.floor(x))
    y1 = int(np.floor(y))
    xs = x - x1
    ys = y - y1
    x1p = nb.int32(x1) * nb.int32(501125321)
    y1p = nb.int32(y1) * nb.int32(1136930381)
    x0p = nb.int32(x1p - nb.int32(501125321))
    y0p = nb.int32(y1p - nb.int32(1136930381))
    x2p = nb.int32(x1p + nb.int32(501125321))
    y2p = nb.int32(y1p + nb.int32(1136930381))
    x3p = nb.int32(x1p + nb.int32(501125321) * nb.int32(2))
    y3p = nb.int32(y1p + nb.int32(1136930381) * nb.int32(2))
    return _cubic_lerp(
        _cubic_lerp(_val_coord(seed, x0p, y0p), _val_coord(seed, x1p, y0p),
                    _val_coord(seed, x2p, y0p), _val_coord(seed, x3p, y0p), xs),
        _cubic_lerp(_val_coord(seed, x0p, y1p), _val_coord(seed, x1p, y1p),
                    _val_coord(seed, x2p, y1p), _val_coord(seed, x3p, y1p), xs),
        _cubic_lerp(_val_coord(seed, x0p, y2p), _val_coord(seed, x1p, y2p),
                    _val_coord(seed, x2p, y2p), _val_coord(seed, x3p, y2p), xs),
        _cubic_lerp(_val_coord(seed, x0p, y3p), _val_coord(seed, x1p, y3p),
                    _val_coord(seed, x2p, y3p), _val_coord(seed, x3p, y3p), xs),
        ys) * (1.0 / (1.5 * 1.5))


# ============================================================================
# Single noise dispatch (maps noise_type int to single function)
# ============================================================================

@njit(fastmath=True, cache=True)
def _apply_single(seed, x, y, noise_type, dist_func, return_type, jitter):
    """
    Dispatch to the correct single-octave noise function.
    x, y must already be coordinate-transformed (frequency * skew for simplex).
    """
    if noise_type == 0:    # OpenSimplex2
        return _single_simplex(seed, x, y)
    elif noise_type == 1:  # OpenSimplex2S
        return _single_opensimplex2s(seed, x, y)
    elif noise_type == 2:  # Cellular
        return _single_cellular(seed, x, y, dist_func, return_type, jitter)
    elif noise_type == 3:  # Perlin
        return _single_perlin(seed, x, y)
    elif noise_type == 4:  # ValueCubic
        return _single_value_cubic(seed, x, y)
    else:                  # Value (5)
        return _single_value(seed, x, y)


# ============================================================================
# Fractal wrappers (match FastNoiseLite's GenFractalFBm, GenFractalRidged,
# GenFractalPingPong exactly, including seed++ per octave)
# ============================================================================

@njit(fastmath=True, cache=True)
def _fractal_noise(seed0, x, y, noise_type, fractal_type,
                   octaves, lacunarity, gain, weighted_strength,
                   ping_pong_strength, fractal_bounding,
                   dist_func, return_type, jitter):
    """
    Evaluate fractal or single noise at one point.
    x, y: pre-transformed coordinates (frequency applied, simplex skew applied).
    Returns a value roughly in [-1, 1].
    """
    if fractal_type == 0:  # NONE
        return _apply_single(nb.int32(seed0), x, y, noise_type, dist_func, return_type, jitter)

    seed = nb.int32(seed0)
    total = 0.0
    amp = fractal_bounding

    if fractal_type == 1:  # FBM
        for _ in range(octaves):
            noise = _apply_single(seed, x, y, noise_type, dist_func, return_type, jitter)
            total += noise * amp
            amp_weight = _lerp(1.0, min(noise + 1.0, 2.0) * 0.5, weighted_strength)
            amp *= amp_weight * gain
            x *= lacunarity
            y *= lacunarity
            seed = nb.int32(seed + nb.int32(1))

    elif fractal_type == 2:  # Ridged
        for _ in range(octaves):
            noise = abs(_apply_single(seed, x, y, noise_type, dist_func, return_type, jitter))
            total += (noise * -2.0 + 1.0) * amp
            amp_weight = _lerp(1.0, 1.0 - noise, weighted_strength)
            amp *= amp_weight * gain
            x *= lacunarity
            y *= lacunarity
            seed = nb.int32(seed + nb.int32(1))

    else:  # PingPong (3)
        for _ in range(octaves):
            raw = _apply_single(seed, x, y, noise_type, dist_func, return_type, jitter)
            noise = _ping_pong((raw + 1.0) * ping_pong_strength)
            total += (noise - 0.5) * 2.0 * amp
            amp_weight = _lerp(1.0, noise, weighted_strength)
            amp *= amp_weight * gain
            x *= lacunarity
            y *= lacunarity
            seed = nb.int32(seed + nb.int32(1))

    return total


# ============================================================================
# Parallel batch function
# ============================================================================

@njit(parallel=True, fastmath=True, cache=True)
def noise2d_batch(
    x: NDArray[np.float64],
    y: NDArray[np.float64],
    seed: int,
    frequency: float,
    noise_type: int,      # 0-5
    fractal_type: int,    # 0-3
    octaves: int,
    lacunarity: float,
    gain: float,
    weighted_strength: float,
    ping_pong_strength: float,
    fractal_bounding: float,
    dist_func: int,       # cellular: 0-3
    return_type: int,     # cellular: 0-6
    jitter: float,        # cellular jitter
) -> NDArray[np.float64]:
    """
    Generate noise for arrays of (x, y) coordinates in parallel.

    Applies frequency scaling and simplex skew (for OpenSimplex2/2S) before
    evaluating the fractal. Returns raw FastNoiseLite values in ~[-1, 1].
    """
    n = len(x)
    out = np.empty(n, dtype=np.float64)
    seed32 = nb.int32(seed)
    use_skew = (noise_type == 0 or noise_type == 1)
    F2 = 0.36602540378443864676372317075294  # 0.5*(sqrt(3)-1)

    for i in prange(n):
        xs = x[i] * frequency
        ys = y[i] * frequency
        if use_skew:
            t = (xs + ys) * F2
            xs += t
            ys += t
        out[i] = _fractal_noise(
            seed32, xs, ys, noise_type, fractal_type,
            octaves, lacunarity, gain, weighted_strength,
            ping_pong_strength, fractal_bounding,
            dist_func, return_type, jitter,
        )
    return out


# ============================================================================
# Domain Warp batch functions
# ============================================================================

@njit(fastmath=True, cache=True)
def _domain_warp_simplex_single(seed, x, y, warp_amp, outgrad_only):
    """Single-point OpenSimplex2 domain warp (matches SingleDomainWarpSimplexGradient)."""
    G2 = 0.21132486540518711774542560974902
    F2 = 0.36602540378443864676372317075294
    t = (x + y) * F2
    xs = x + t
    ys = y + t
    i = int(np.floor(xs))
    j = int(np.floor(ys))
    xi = xs - i
    yi = ys - j
    t2 = (xi + yi) * G2
    x0 = xi - t2
    y0 = yi - t2
    ip = nb.int32(i) * nb.int32(501125321)
    jp = nb.int32(j) * nb.int32(1136930381)
    vx = 0.0
    vy = 0.0
    a = 0.5 - x0 * x0 - y0 * y0
    if a > 0.0:
        aaaa = (a * a) * (a * a)
        if outgrad_only:
            xo, yo = _grad_coord_out(seed, ip, jp)
        else:
            xo, yo = _grad_coord_dual(seed, ip, jp, x0, y0)
        vx += aaaa * xo
        vy += aaaa * yo
    c_val = (2.0 * (1.0 - 2.0 * G2) * (1.0 / G2 - 2.0)) * t2 + ((-2.0 * (1.0 - 2.0 * G2) * (1.0 - 2.0 * G2)) + a)
    if c_val > 0.0:
        x2 = x0 + (2.0 * G2 - 1.0)
        y2 = y0 + (2.0 * G2 - 1.0)
        cccc = (c_val * c_val) * (c_val * c_val)
        if outgrad_only:
            xo, yo = _grad_coord_out(seed, nb.int32(ip + nb.int32(501125321)), nb.int32(jp + nb.int32(1136930381)))
        else:
            xo, yo = _grad_coord_dual(seed, nb.int32(ip + nb.int32(501125321)), nb.int32(jp + nb.int32(1136930381)), x2, y2)
        vx += cccc * xo
        vy += cccc * yo
    if y0 > x0:
        x1 = x0 + G2
        y1 = y0 + (G2 - 1.0)
        b = 0.5 - x1 * x1 - y1 * y1
        if b > 0.0:
            bbbb = (b * b) * (b * b)
            if outgrad_only:
                xo, yo = _grad_coord_out(seed, ip, nb.int32(jp + nb.int32(1136930381)))
            else:
                xo, yo = _grad_coord_dual(seed, ip, nb.int32(jp + nb.int32(1136930381)), x1, y1)
            vx += bbbb * xo
            vy += bbbb * yo
    else:
        x1 = x0 + (G2 - 1.0)
        y1 = y0 + G2
        b = 0.5 - x1 * x1 - y1 * y1
        if b > 0.0:
            bbbb = (b * b) * (b * b)
            if outgrad_only:
                xo, yo = _grad_coord_out(seed, nb.int32(ip + nb.int32(501125321)), jp)
            else:
                xo, yo = _grad_coord_dual(seed, nb.int32(ip + nb.int32(501125321)), jp, x1, y1)
            vx += bbbb * xo
            vy += bbbb * yo
    return vx * warp_amp, vy * warp_amp


@njit(fastmath=True, cache=True)
def _domain_warp_basic_grid_single(seed, x, y, warp_amp, frequency):
    """Single-point Basic Grid domain warp (matches SingleDomainWarpBasicGrid)."""
    xf = x * frequency
    yf = y * frequency
    x0 = int(np.floor(xf))
    y0 = int(np.floor(yf))
    xs = _interp_hermite(xf - x0)
    ys = _interp_hermite(yf - y0)
    x0p = nb.int32(x0) * nb.int32(501125321)
    y0p = nb.int32(y0) * nb.int32(1136930381)
    x1p = nb.int32(x0p + nb.int32(501125321))
    y1p = nb.int32(y0p + nb.int32(1136930381))
    h00 = int(_hash2d(seed, x0p, y0p)) & 510
    h10 = int(_hash2d(seed, x1p, y0p)) & 510
    lx0x = _lerp(nb.float64(_RAND_VECS_2D[h00]), nb.float64(_RAND_VECS_2D[h10]), xs)
    ly0x = _lerp(nb.float64(_RAND_VECS_2D[h00 | 1]), nb.float64(_RAND_VECS_2D[h10 | 1]), xs)
    h01 = int(_hash2d(seed, x0p, y1p)) & 510
    h11 = int(_hash2d(seed, x1p, y1p)) & 510
    lx1x = _lerp(nb.float64(_RAND_VECS_2D[h01]), nb.float64(_RAND_VECS_2D[h11]), xs)
    ly1x = _lerp(nb.float64(_RAND_VECS_2D[h01 | 1]), nb.float64(_RAND_VECS_2D[h11 | 1]), xs)
    return _lerp(lx0x, lx1x, ys) * warp_amp, _lerp(ly0x, ly1x, ys) * warp_amp


@njit(parallel=True, fastmath=True, cache=True)
def domain_warp_2d_batch(
    x: NDArray[np.float64],
    y: NDArray[np.float64],
    seed: int,
    warp_type: int,      # 0=OpenSimplex2, 1=OpenSimplex2Reduced, 2=BasicGrid
    amplitude: float,
    frequency: float,
    fractal_type: int,   # 0=None, 1=Progressive, 2=Independent
    octaves: int,
    lacunarity: float,
    gain: float,
    fractal_bounding: float,
) -> tuple:
    """Apply domain warp to coordinate arrays. Returns (warped_x, warped_y)."""
    n = len(x)
    out_x = np.empty(n, dtype=np.float64)
    out_y = np.empty(n, dtype=np.float64)

    for i in prange(n):
        xi = x[i]
        yi = y[i]

        if fractal_type == 0:  # NONE
            seed32 = nb.int32(seed)
            if warp_type == 2:  # BasicGrid
                amp = amplitude * fractal_bounding
                dx, dy = _domain_warp_basic_grid_single(seed32, xi, yi, amp, frequency)
            elif warp_type == 1:  # OpenSimplex2Reduced
                amp = amplitude * fractal_bounding * 16.0
                dx, dy = _domain_warp_simplex_single(seed32, xi * frequency, yi * frequency, amp, True)
            else:  # OpenSimplex2
                amp = amplitude * fractal_bounding * 38.283687591552734375
                dx, dy = _domain_warp_simplex_single(seed32, xi * frequency, yi * frequency, amp, False)
            out_x[i] = xi + dx
            out_y[i] = yi + dy

        elif fractal_type == 1:  # PROGRESSIVE
            seed32 = nb.int32(seed)
            amp = amplitude * fractal_bounding
            freq = frequency
            wx = xi
            wy = yi
            for _ in range(octaves):
                if warp_type == 2:
                    dx, dy = _domain_warp_basic_grid_single(seed32, wx, wy, amp, freq)
                elif warp_type == 1:
                    dx, dy = _domain_warp_simplex_single(seed32, wx * freq, wy * freq, amp * 16.0, True)
                else:
                    dx, dy = _domain_warp_simplex_single(seed32, wx * freq, wy * freq, amp * 38.283687591552734375, False)
                wx += dx
                wy += dy
                seed32 = nb.int32(seed32 + nb.int32(1))
                amp *= gain
                freq *= lacunarity
            out_x[i] = wx
            out_y[i] = wy

        else:  # INDEPENDENT (2)
            seed32 = nb.int32(seed)
            amp = amplitude * fractal_bounding
            freq = frequency
            total_dx = 0.0
            total_dy = 0.0
            for _ in range(octaves):
                if warp_type == 2:
                    dx, dy = _domain_warp_basic_grid_single(seed32, xi, yi, amp, freq)
                elif warp_type == 1:
                    dx, dy = _domain_warp_simplex_single(seed32, xi * freq, yi * freq, amp * 16.0, True)
                else:
                    dx, dy = _domain_warp_simplex_single(seed32, xi * freq, yi * freq, amp * 38.283687591552734375, False)
                total_dx += dx
                total_dy += dy
                seed32 = nb.int32(seed32 + nb.int32(1))
                amp *= gain
                freq *= lacunarity
            out_x[i] = xi + total_dx
            out_y[i] = yi + total_dy

    return out_x, out_y