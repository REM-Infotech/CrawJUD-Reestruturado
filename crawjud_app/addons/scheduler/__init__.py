"""Provide database-driven task scheduling functionality for the CrawJUD-Bots celery worker."""

import json
import re
from typing import Any, Union

from celery import Celery
from celery.app.utils import Settings
from celery.beat import ScheduleEntry, Scheduler
from celery.loaders.base import BaseLoader
from celery.schedules import crontab
from quart import current_app as app


class DatabaseScheduler(Scheduler):
    """Manage Celery task schedules using database-stored configurations.

    This scheduler extends the base Celery Scheduler to load task schedules from a database,
    enabling dynamic schedule updates without requiring application restarts.

    Attributes:
        _schedule (dict): Internal cache of current schedule entries.

    """

    @classmethod
    def fix_unicode(cls, text: str) -> str:
        """Convert escaped unicode sequences to proper unicode characters.

        Args:
            text (str): The text containing escaped unicode sequences (e.g., "u00ae").

        Returns:
            str: Text with properly decoded unicode characters.

        Example:
            >>> DatabaseScheduler.fix_unicode("Hello u00ae World")
            'Hello ® World'

        """
        return (
            re.sub(r"u00([0-9a-fA-F]{2})", r"\\u00\1", text)
            .encode()
            .decode("unicode_escape")
        )

    def __init__(
        self,
        *args: str | int,
        **kwargs: str | int,
    ) -> None:
        """Initialize a new DatabaseScheduler instance.

        Args:
            *args: Variable positional arguments passed to parent Scheduler.
            **kwargs: Variable keyword arguments passed to parent Scheduler.

        """
        super().__init__(*args, **kwargs)
        self._schedule = {}

    def get_schedule(self) -> dict:
        """Retrieve and construct schedule entries from the database.

        Queries the database for all schedule entries and converts them into Celery ScheduleEntry
        objects with their associated crontab schedules.

        Returns:
            dict: Mapping of task names to their corresponding ScheduleEntry objects.

        Note:
            The schedule entries include task name, schedule (as crontab), arguments, and keyword
            arguments loaded from the database.

        """
        schedules = {}

        from api.models import CrontabModel, ScheduleModel

        db_entries: list[ScheduleModel] = ScheduleModel.query.all()
        for entry in db_entries:
            cron_args = {}
            old_cron_args: CrontabModel = entry.schedule
            cron_args_items = list(old_cron_args.__dict__.items())
            for key, value in cron_args_items:
                if (not key.startswith("_")) and key != "schedule" and key != "id":
                    cron_args.update({key: value})

            # if entry.name not unicode, fix it
            name_custom = DatabaseScheduler.fix_unicode(entry.name)
            schedules[entry.task] = ScheduleEntry(
                name=name_custom,
                task=entry.task,
                schedule=crontab(**cron_args),
                args=json.loads(entry.args or "[]"),
                kwargs=json.loads(entry.kwargs or "{}"),
            )
        return schedules

    @staticmethod
    def parse_cron(cron_string: str) -> dict[str, any]:
        """Convert a cron string into a dictionary of schedule components.

        Splits a standard cron string into its constituent parts and maps them to their
        corresponding schedule fields.

        Args:
            cron_string (str): Space-separated cron schedule (e.g., "* * * * *").

        Returns:
            dict: Mapping of cron components to their values.
                Keys: minute, hour, day_of_month, month_of_year, day_of_week.

        Example:
            >>> DatabaseScheduler.parse_cron("0 12 * * *")
            {'minute': '0', 'hour': '12', 'day_of_month': '*', 'month_of_year': '*', 'day_of_week': '*'}

        """
        fields = ["minute", "hour", "day_of_month", "month_of_year", "day_of_week"]
        cron_parts = cron_string.split()
        return dict(zip(fields, cron_parts, strict=False))

    @property
    def schedule(self) -> dict:
        """Access the current task schedule.

        Ensures the schedule is synchronized with the database before returning it.

        Returns:
            dict: The current mapping of task names to ScheduleEntry objects.

        Note:
            This property triggers a database sync on each access to ensure schedule freshness.

        """
        self.sync()
        return self._schedule

    def sync(self) -> None:
        """Update the internal schedule cache with the latest database entries.

        Refreshes the internal schedule dictionary by fetching the most recent schedule
        configurations from the database.
        """
        self._schedule = self.get_schedule()

    def tick(self) -> int | Any:
        """Process scheduled tasks and determine the next execution time.

        Processes any due tasks, updates the schedule from the database, and calculates
        the time until the next task needs to run.

        Returns:
            Union[int, Any]: Number of seconds until the next scheduled task execution.

        Note:
            This method is called periodically by the Celery beat service to maintain
            the scheduler's operation.

        """
        remaining_times = super().tick()
        self.sync()
        return remaining_times
