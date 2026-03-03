"""
CharacterController / PlayerController

CharacterController
-------------------
Controlador base para cualquier personaje del juego (jugador, NPC,
enemigo, aliado…).  Gestiona:

- Movimiento libre (píxeles) o en grid (A*).
- Inventario: recoger, soltar, usar ítems.
- Equipamiento: slots con validación de tipo.
- Interacción con entidades del entorno dentro de un radio configurable.
- Hooks sobreescribibles para reaccionar a cada acción.

El controller se asigna como componente del propio personaje::

    npc.controller = CharacterController(npc)

Desde ese momento ``BaseCharacter.update()`` llama automáticamente a
``controller.tick(delta_time)`` en cada frame, sin necesidad de gestión
externa.

PlayerController
----------------
Subclase de CharacterController para el personaje humano.  Añade la
lectura de input de pygame.  El input se pasa manualmente cada frame::

    player.controller = PlayerController(player)
    # en el bucle principal:
    player.controller.handle_input(pygame.key.get_pressed())
    player.update(delta_time)   # ← esto ya dispara el tick interno

Uso básico — NPC / IA
---------------------
    npc.controller = CharacterController(npc)
    # la IA llama directamente a los métodos de acción:
    npc.controller.move_to_grid((tx, ty))
    npc.controller.interact_with(player)
    # npc.update(delta_time) hace el tick automáticamente
"""

from __future__ import annotations

import math
from typing import Any, Dict, Optional, Tuple

import pygame

from core.character.base import BaseCharacter
from core.item.inventory import Inventory
from core.item.item import BaseItem, ItemType

GridPos = Tuple[int, int]


# ---------------------------------------------------------------------------
# Protocolo de interactuable
# ---------------------------------------------------------------------------

class Interactable:
    """
    Mixin / protocolo ligero para objetos con los que el jugador puede
    interactuar (NPCs, cofres, puertas, palancas, etc.).

    Implementa ``interact(actor)`` en tus entidades para que el controlador
    pueda invocarlos automáticamente.
    """

    def interact(self, actor: "BaseCharacter") -> bool:
        """
        Lógica de interacción con *actor*.

        Returns:
            True si la interacción tuvo efecto.
        """
        return False

    def get_interaction_label(self) -> str:
        """Texto de acción que puede mostrarse en UI (p. ej. "Abrir cofre")."""
        return "Interactuar"


# ---------------------------------------------------------------------------
# Slots de equipo
# ---------------------------------------------------------------------------

class EquipSlot:
    """
    Representación de un único slot de equipamiento.

    Attributes:
        name:           Identificador del slot (p. ej. ``"main_hand"``).
        allowed_types:  Tipos de ítem aceptados.  ``None`` → sin restricción.
        item:           Ítem equipado actualmente, o ``None``.
    """

    def __init__(
        self,
        name: str,
        allowed_types: Optional[list[ItemType]] = None,
    ) -> None:
        self.name: str = name
        self.allowed_types: Optional[set[ItemType]] = (
            set(allowed_types) if allowed_types else None
        )
        self.item: Optional[BaseItem] = None

    @property
    def is_empty(self) -> bool:
        return self.item is None

    def accepts(self, item: BaseItem) -> bool:
        """True si *item* puede ir en este slot."""
        if self.allowed_types is None:
            return True
        return bool(self.allowed_types.intersection(item.item_type))

    def __repr__(self) -> str:
        return f"<EquipSlot '{self.name}': {self.item!r}>"



# ---------------------------------------------------------------------------
# CharacterController  (base — jugador y no-jugador)
# ---------------------------------------------------------------------------

class CharacterController:
    """
    Controlador base para cualquier personaje del juego.

    Puede usarse directamente por una IA llamando a los métodos de acción,
    o como superclase de ``PlayerController`` para el personaje humano.

    Parameters
    ----------
    character:
        Personaje controlado.  Debe ser una instancia de ``BaseCharacter``
        o una subclase.
    inventory:
        Inventario del personaje.  Se crea uno vacío si no se proporciona.
    interact_range:
        Radio en píxeles dentro del cual el personaje puede interactuar
        con entidades.
    grid_mode:
        Si ``True`` el movimiento se realiza celda a celda (A*).
        Si ``False`` se usa movimiento libre por píxeles.
    equip_slots:
        Lista de tuplas ``(nombre, [tipos_permitidos])`` para definir
        los slots de equipo.  Si es ``None`` se usan los predefinidos.
    """

    # Slots de equipamiento predefinidos (sobreescribibles al construir)
    DEFAULT_EQUIP_SLOTS: list[tuple[str, Optional[list[ItemType]]]] = [
        ("main_hand",  [ItemType.WEAPON, ItemType.TOOL]),
        ("off_hand",   [ItemType.WEAPON, ItemType.TOOL, ItemType.ACCESSORY]),
        ("head",       [ItemType.ARMOR]),
        ("chest",      [ItemType.ARMOR]),
        ("legs",       [ItemType.ARMOR]),
        ("accessory",  [ItemType.ACCESSORY]),
    ]

    def __init__(
        self,
        character: BaseCharacter,
        inventory: Optional[Inventory] = None,
        interact_range: float = 64.0,
        grid_mode: bool = False,
        equip_slots: Optional[list[tuple[str, Optional[list[ItemType]]]]] = None,
    ) -> None:
        self.character: BaseCharacter = character
        self.inventory: Inventory = inventory if inventory is not None else Inventory()
        self.interact_range: float = interact_range
        self.grid_mode: bool = grid_mode

        # Índice del ítem seleccionado en el inventario
        self._selected_index: int = 0

        # Slots de equipamiento
        slot_defs = equip_slots if equip_slots is not None else self.DEFAULT_EQUIP_SLOTS
        self.equip_slots: Dict[str, EquipSlot] = {
            name: EquipSlot(name, types) for name, types in slot_defs
        }


    # ------------------------------------------------------------------
    # Acceso rápido
    # ------------------------------------------------------------------

    @property
    def selected_item(self) -> Optional[BaseItem]:
        """Ítem actualmente seleccionado en el inventario."""
        items = self.inventory.items
        if not items:
            return None
        self._selected_index = min(self._selected_index, len(items) - 1)
        return items[self._selected_index]

    @property
    def position(self) -> Tuple[float, float]:
        """Posición del personaje en píxeles."""
        return self.character.x, self.character.y

    # ------------------------------------------------------------------
    # Movimiento — API para IA / scripts
    # ------------------------------------------------------------------

    def move_towards(self, direction_x: float, direction_y: float) -> None:
        """
        Mueve el personaje en la dirección dada (modo libre).

        Los valores se normalizan automáticamente si son diagonales.

        Parameters
        ----------
        direction_x:
            Componente horizontal (-1 izquierda … +1 derecha).
        direction_y:
            Componente vertical (-1 arriba … +1 abajo).
        """
        if direction_x != 0 and direction_y != 0:
            factor = 1.0 / math.sqrt(2.0)
            direction_x *= factor
            direction_y *= factor

        if direction_x != 0 or direction_y != 0:
            self.character.move(direction_x, direction_y)
            self.on_move(direction_x, direction_y)
        else:
            self.character.stop()

    def move_to_grid(self, destination: GridPos) -> bool:
        """
        Ordena al personaje moverse a *destination* por A* (modo grid).

        Returns
        -------
        bool
            ``True`` si se encontró un camino válido.
        """
        moved = self.character.move_to(destination)
        if moved:
            self.on_move_grid(destination)
        return moved

    def stop(self) -> None:
        """Detiene el movimiento del personaje."""
        self.character.stop()
        self.character.stop_grid_movement()

    # ------------------------------------------------------------------
    # Tick — llamado automáticamente desde BaseCharacter.update()
    # ------------------------------------------------------------------

    def tick(self, delta_time: float) -> None:
        """
        Lógica por frame del controller.

        ``BaseCharacter.update()`` llama a este mét\odo automáticamente
        cuando el controller está asignado al personaje.  No es necesario
        llamarlo a mano salvo que el personaje no tenga su propio bucle de
        actualización.

        Override en subclases para añadir lógica de IA u otras acciones
        por frame.

        Parameters
        ----------
        delta_time:
            Tiempo en segundos desde el último frame.
        """

    # ------------------------------------------------------------------
    # Inventario
    # ------------------------------------------------------------------

    def pick_up_item(self, item: BaseItem) -> bool:
        """
        Intenta añadir *item* al inventario del jugador.

        Returns
        -------
        bool
            ``True`` si el ítem se añadió correctamente.
        """
        if not self.inventory.can_add(item):
            self.on_inventory_full(item)
            return False
        result = self.inventory.add(item)
        if result:
            self.on_item_picked_up(item)
        return result

    def drop_selected_item(self) -> bool:
        """
        Suelta el ítem seleccionado en la posición actual del jugador.

        Returns
        -------
        bool
            ``True`` si el ítem se soltó correctamente.
        """
        item = self.selected_item
        if item is None:
            return False
        x, y = self.position
        result = self.inventory.drop(item, x, y)
        if result:
            self.on_item_dropped(item)
        return result

    def drop_item(
        self,
        item: BaseItem,
        x: Optional[float] = None,
        y: Optional[float] = None,
    ) -> bool:
        """
        Suelta *item* en (x, y).  Si no se especifica posición, usa la del jugador.

        Returns
        -------
        bool
            ``True`` si el ítem se soltó correctamente.
        """
        if x is None or y is None:
            x, y = self.position
        if item not in self.inventory:
            return False
        result = self.inventory.drop(item, x, y)
        if result:
            self.on_item_dropped(item)
        return result

    def use_selected_item(self) -> bool:
        """
        Usa el ítem actualmente seleccionado en el inventario.

        Returns
        -------
        bool
            ``True`` si el ítem se usó con éxito.
        """
        item = self.selected_item
        if item is None:
            return False
        return self.use_item(item)

    def use_item(self, item: BaseItem) -> bool:
        """
        Usa *item* (debe estar en el inventario).

        Returns
        -------
        bool
            ``True`` si el ítem se usó con éxito.
        """
        if item not in self.inventory:
            return False
        result = item.use(self.character)
        if result:
            self.on_item_used(item)
        return result

    def select_item(self, index: int) -> Optional[BaseItem]:
        """
        Selecciona el ítem en la posición *index* del inventario.

        Returns
        -------
        Optional[BaseItem]
            El ítem seleccionado, o ``None`` si el índice está fuera de rango.
        """
        items = self.inventory.items
        if not items:
            return None
        self._selected_index = max(0, min(index, len(items) - 1))
        return items[self._selected_index]

    # ------------------------------------------------------------------
    # Equipamiento
    # ------------------------------------------------------------------

    def equip_item(self, item: BaseItem, slot_name: str) -> bool:
        """
        Equipa *item* en el slot *slot_name*.

        El ítem debe estar en el inventario.  Si el slot ya tiene un ítem
        equipado, se desequipa primero (vuelve al inventario).

        Returns
        -------
        bool
            ``True`` si el equipamiento tuvo éxito.
        """
        if item not in self.inventory:
            return False

        slot = self.equip_slots.get(slot_name)
        if slot is None:
            return False

        if not slot.accepts(item):
            self.on_equip_failed(item, slot_name, reason="tipo no permitido")
            return False

        # Desequipar el ítem actual si lo hay
        if not slot.is_empty:
            self._do_unequip(slot)

        result = item.equip(self.character)
        if result:
            slot.item = item
            self.on_item_equipped(item, slot_name)
        return result

    def unequip_item(self, slot_name: str) -> Optional[BaseItem]:
        """
        Desequipa el ítem del slot *slot_name* y lo devuelve al inventario.

        Returns
        -------
        Optional[BaseItem]
            El ítem desequipado, o ``None`` si el slot estaba vacío o
            la operación falló.
        """
        slot = self.equip_slots.get(slot_name)
        if slot is None or slot.is_empty:
            return None
        return self._do_unequip(slot)

    def _do_unequip(self, slot: EquipSlot) -> Optional[BaseItem]:
        """Lógica interna de desequipado."""
        item = slot.item
        if item is None:
            return None
        result = item.unequip()
        if result:
            slot.item = None
            self.on_item_unequipped(item, slot.name)
        return item if result else None

    def get_equipped(self, slot_name: str) -> Optional[BaseItem]:
        """
        Devuelve el ítem equipado en *slot_name*, o ``None`` si está vacío.
        """
        slot = self.equip_slots.get(slot_name)
        return slot.item if slot else None

    # ------------------------------------------------------------------
    # Interacción con el entorno
    # ------------------------------------------------------------------

    def try_interact(self, candidates: Optional[list] = None) -> bool:
        """
        Intenta interactuar con la entidad más cercana dentro del rango.

        Parameters
        ----------
        candidates:
            Lista de objetos candidatos.  Si es ``None`` se llama a
            ``get_interactables()`` para obtenerlos.

        Returns
        -------
        bool
            ``True`` si se produjo una interacción.
        """
        if candidates is None:
            candidates = self.get_interactables()

        target = self._nearest_interactable(candidates)
        if target is None:
            return False

        result = target.interact(self.character)
        if result:
            self.on_interaction(target)
        return result

    def interact_with(self, entity: Any) -> bool:
        """
        Interactúa directamente con *entity* (sin comprobar distancia).

        Útil para interacciones activadas por UI o scripts.

        Returns
        -------
        bool
            ``True`` si la interacción tuvo efecto.
        """
        if not hasattr(entity, "interact"):
            return False
        result = entity.interact(self.character)
        if result:
            self.on_interaction(entity)
        return result

    def _nearest_interactable(self, candidates: list) -> Optional[Any]:
        """Devuelve el candidato más cercano con ``interact()`` dentro del rango."""
        px, py = self.position
        best: Optional[Any] = None
        best_dist = float("inf")
        for obj in candidates:
            if not hasattr(obj, "interact"):
                continue
            ox = getattr(obj, "x", getattr(obj, "grid_x", 0))
            oy = getattr(obj, "y", getattr(obj, "grid_y", 0))
            dist = math.hypot(px - ox, py - oy)
            if dist <= self.interact_range and dist < best_dist:
                best = obj
                best_dist = dist
        return best

    # ------------------------------------------------------------------
    # get_interactables — override para integrarlo con la escena
    # ------------------------------------------------------------------

    def get_interactables(self) -> list:
        """
        Devuelve la lista de entidades candidatas a interacción.

        Por defecto devuelve una lista vacía.  Override este mét\odo o
        asigna::

            controller.get_interactables = lambda: scene.entities

        para integrarlo con tu escena.
        """
        return []

    # ------------------------------------------------------------------
    # Hooks — sobreescribir en subclases para reaccionar a eventos
    # ------------------------------------------------------------------

    def on_move(self, dx: float, dy: float) -> None:
        """Llamado cuando el personaje se mueve en modo libre."""

    def on_move_grid(self, target: GridPos) -> None:
        """Llamado cuando se inicia un paso en modo grid."""

    def on_item_picked_up(self, item: BaseItem) -> None:
        """Llamado tras recoger un ítem con éxito."""

    def on_item_dropped(self, item: BaseItem) -> None:
        """Llamado tras soltar un ítem con éxito."""

    def on_item_used(self, item: BaseItem) -> None:
        """Llamado tras usar un ítem con éxito."""

    def on_item_equipped(self, item: BaseItem, slot_name: str) -> None:
        """Llamado tras equipar un ítem con éxito."""

    def on_item_unequipped(self, item: BaseItem, slot_name: str) -> None:
        """Llamado tras desequipar un ítem."""

    def on_equip_failed(self, item: BaseItem, slot_name: str, reason: str = "") -> None:
        """Llamado cuando el equipamiento falla."""

    def on_inventory_full(self, item: BaseItem) -> None:
        """Llamado cuando el inventario no puede aceptar un ítem."""

    def on_interaction(self, entity: Any) -> None:
        """Llamado tras una interacción exitosa con una entidad."""

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        mode = "grid" if self.grid_mode else "free"
        return (
            f"<{self.__class__.__name__} character={self.character.name!r} "
            f"mode={mode} inventory={self.inventory!r}>"
        )


# ---------------------------------------------------------------------------
# PlayerController  (subclase — personaje controlado por el jugador)
# ---------------------------------------------------------------------------

class PlayerController(CharacterController):
    """
    Controlador para el personaje manejado por el jugador humano.

    Extiende ``CharacterController`` con:

    - Lectura de input de pygame (``handle_input``).
    - Mapa de teclas configurable.
    - Detección de "just pressed" para evitar disparos repetidos.

    Parameters
    ----------
    character:
        Personaje controlado.
    inventory:
        Inventario del jugador.  Se crea uno vacío si no se proporciona.
    interact_range:
        Radio de interacción en píxeles.
    grid_mode:
        ``True`` → movimiento celda a celda.  ``False`` → movimiento libre.
    key_map:
        Diccionario de acción → ``pygame.K_*``.  Se fusiona con
        ``DEFAULT_KEY_MAP``; solo hay que pasar las teclas que cambien.
    equip_slots:
        Slots de equipo personalizados.  ``None`` usa los predefinidos.
    """

    DEFAULT_KEY_MAP: Dict[str, int] = {
        "up":        pygame.K_w,
        "down":      pygame.K_s,
        "left":      pygame.K_a,
        "right":     pygame.K_d,
        "interact":  pygame.K_e,
        "use_item":  pygame.K_f,
        "drop_item": pygame.K_g,
    }

    def __init__(
        self,
        character: BaseCharacter,
        inventory: Optional[Inventory] = None,
        interact_range: float = 64.0,
        grid_mode: bool = False,
        key_map: Optional[Dict[str, int]] = None,
        equip_slots: Optional[list[tuple[str, Optional[list[ItemType]]]]] = None,
    ) -> None:
        super().__init__(
            character=character,
            inventory=inventory,
            interact_range=interact_range,
            grid_mode=grid_mode,
            equip_slots=equip_slots,
        )
        # Merge del mapa de teclas personalizado sobre el predefinido
        self.key_map: Dict[str, int] = {**self.DEFAULT_KEY_MAP, **(key_map or {})}

        # Estado de teclas del frame anterior (para detectar "just pressed")
        self._prev_keys: Dict[str, bool] = {k: False for k in self.key_map}

    # ------------------------------------------------------------------
    # Loop principal
    # ------------------------------------------------------------------

    def handle_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        """
        Procesa el estado de teclas de pygame y ejecuta las acciones
        correspondientes.

        Llama a este mét\odo una vez por frame pasándole
        ``pygame.key.get_pressed()``.

        Parameters
        ----------
        keys:
            Resultado de ``pygame.key.get_pressed()``.
        """
        self._handle_movement(keys)
        self._handle_actions(keys)
        self._update_prev_keys(keys)

    # ------------------------------------------------------------------
    # Movimiento por teclado
    # ------------------------------------------------------------------

    def _handle_movement(self, keys: pygame.key.ScancodeWrapper) -> None:
        """Delega al modo de movimiento activo."""
        if self.grid_mode:
            self._handle_grid_movement(keys)
        else:
            self._handle_free_movement(keys)

    def _handle_free_movement(self, keys: pygame.key.ScancodeWrapper) -> None:
        """Traduce teclas a dirección y llama a ``move_towards``."""
        dx = dy = 0.0
        if keys[self.key_map["left"]]:
            dx -= 1.0
        if keys[self.key_map["right"]]:
            dx += 1.0
        if keys[self.key_map["up"]]:
            dy -= 1.0
        if keys[self.key_map["down"]]:
            dy += 1.0
        self.move_towards(dx, dy)

    def _handle_grid_movement(self, keys: pygame.key.ScancodeWrapper) -> None:
        """Traduce teclas a paso de celda; espera a que el paso anterior termine."""
        if self.character._movement and self.character._movement.is_moving:
            return

        gx, gy = self.character.grid_position
        target: Optional[GridPos] = None

        if keys[self.key_map["left"]]:
            target = (gx - 1, gy)
        elif keys[self.key_map["right"]]:
            target = (gx + 1, gy)
        elif keys[self.key_map["up"]]:
            target = (gx, gy - 1)
        elif keys[self.key_map["down"]]:
            target = (gx, gy + 1)

        if target is not None:
            self.move_to_grid(target)

    # ------------------------------------------------------------------
    # Acciones por teclado (un solo disparo por pulsación)
    # ------------------------------------------------------------------

    def _handle_actions(self, keys: pygame.key.ScancodeWrapper) -> None:
        """Detecta pulsaciones nuevas y ejecuta acciones."""
        if self._just_pressed(keys, "interact"):
            self.try_interact()
        if self._just_pressed(keys, "use_item"):
            self.use_selected_item()
        if self._just_pressed(keys, "drop_item"):
            self.drop_selected_item()

    def _just_pressed(self, keys: pygame.key.ScancodeWrapper, action: str) -> bool:
        """``True`` solo en el primer frame en que se pulsa *action*."""
        current = bool(keys[self.key_map[action]])
        return current and not self._prev_keys.get(action, False)

    def _update_prev_keys(self, keys: pygame.key.ScancodeWrapper) -> None:
        for action, key in self.key_map.items():
            self._prev_keys[action] = bool(keys[key])


