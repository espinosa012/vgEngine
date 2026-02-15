import enum

class WorldParameterName(enum):
    GlobalSeed = 0
    WorldSizeX = 1
    WorldSizeY = 2
    EquatorLatitude = 3
    MinContinentalHeight = 4
    PeaksAndValleysScale = 5
    ContinentalScale = 6
    SeaScale = 7
    SeaElevationThreshold = 8
    IslandScale = 9
    VolcanicIslandScale = 10
    IslandThreshold = 11
    OutToSeaFactor = 12

class WorldMatrixName(enum):
    pass

class WorldGenerationStage(enum):
    Latitude = 0
    Elevation = 1
    River = 2
    Temperature = 3




class VGWorld:

    def __init__(self, name):
        pass

    def run_generation_pipeline(self):
        pass

    def run_generation_stage(self, stage: WorldGenerationStage):
        pass
