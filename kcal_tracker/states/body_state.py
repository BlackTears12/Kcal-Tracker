import datetime
import reflex as rx
from kcal_tracker.data.body import MeasurementInput, SiteSummary, normalize_site
from kcal_tracker.models.services import BodyService
from kcal_tracker.states.login_state import acting_user_id
from kcal_tracker.states.nutrition_state import NutritionState


class BodyState(rx.State):
    summaries: list[SiteSummary] = []
    # Site whose history is unfolded in the list, empty for none
    expanded_site: str = ""

    @rx.var
    def site_count(self) -> int:
        return len(self.summaries)

    # Event handlers
    async def load(self):
        user_id = await acting_user_id(self)
        if user_id is None:
            return
        self._reload(user_id)

    def toggle_site(self, site: str):
        self.expanded_site = "" if self.expanded_site == site else site

    async def remove_measurement(self, site: str, date_iso: str):
        user_id = await acting_user_id(self)
        if user_id is None:
            return
        BodyService(user_id).remove(site, datetime.date.fromisoformat(date_iso))
        self._reload(user_id)

    # Utilities, private so the client can't call them with another user's id
    def _reload(self, user_id: str):
        self.summaries = BodyService(user_id).summary()


class BodyDialogState(rx.State):
    show_modal: bool = False
    rows: list[MeasurementInput] = []
    new_site: str = ""

    def set_show_modal(self, val: bool):
        self.show_modal = val

    def set_row_value(self, index: int, val: str):
        items = self.rows
        if 0 <= index < len(items):
            items[index].value = val
            self.rows = items

    def set_new_site(self, val: str):
        self.new_site = val

    def add_custom_site(self):
        site = normalize_site(self.new_site)
        if site and site.lower() not in [r.site.lower() for r in self.rows]:
            self.rows = self.rows + [MeasurementInput(site=site)]
        self.new_site = ""

    async def open_modal(self):
        """Opens the dialog for the viewed day, prefilled with what's already logged for it."""
        user_id = await acting_user_id(self)
        if user_id is None:
            return
        service = BodyService(user_id)
        day = (await self.get_state(NutritionState)).date_context
        logged = service.on(day)
        self.rows = [MeasurementInput(site=site, value=f"{logged[site]:g}" if site in logged else "")
                     for site in service.sites()]
        self.new_site = ""
        self.show_modal = True

    def close_modal(self):
        self.show_modal = False

    async def save(self):
        user_id = await acting_user_id(self)
        if user_id is None:
            return
        values: dict[str, float | None] = {}
        for row in self.rows:
            try:
                values[row.site] = float(row.value) if row.value.strip() else None
            except ValueError:
                values[row.site] = None
        day = (await self.get_state(NutritionState)).date_context
        BodyService(user_id).set_day(day, values)
        (await self.get_state(BodyState))._reload(user_id)
        self.show_modal = False
