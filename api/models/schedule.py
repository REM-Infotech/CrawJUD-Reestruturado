"""Defines schedule-related models for the CrawJUD-Bots application.

Includes scheduled jobs and their corresponding crontab configurations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from crawjud.api import db

if TYPE_CHECKING:
    from datetime import datetime


class ScheduleModel(db.Model):
    """Represents a scheduled job with execution details.

    Attributes:
        id (int): Primary key for the scheduled job.
        name (str): Name of the job or task.
        task (str): Task identifier to be executed.
        email (str): Email address for notifications (optional).
        schedule_id (int): References the crontab configuration.
        args (str): JSON string of positional arguments.
        kwargs (str): JSON string of keyword arguments.
        last_run_at (datetime): Timestamp of the last execution.
        license_id (int): Foreign key referencing the license.
        user_id (int): Foreign key referencing the user who created the job.

    """

    __tablename__ = "scheduled_jobs"
    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(128), nullable=False)
    task: str = db.Column(db.String(128), nullable=False)
    email: str = db.Column(db.String(128), nullable=True)

    schedule_id = db.Column(
        db.Integer,
        db.ForeignKey("crontab_model.id"),
        nullable=False,
    )
    schedule = db.relationship("CrontabModel", backref="schedule", lazy=True)

    args: str = db.Column(
        db.Text,
        nullable=True,
        default="[]",
    )  # JSON para argumentos

    kwargs: str = db.Column(db.Text, nullable=True, default="{}")  # JSON para kwargs
    last_run_at: datetime = db.Column(db.DateTime, nullable=True)

    license_id: int = db.Column(db.Integer, db.ForeignKey("licenses_users.id"))
    license_usr = db.relationship(
        "LicensesUsers",
        backref=db.backref("scheduled_execution", lazy=True),
    )

    user_id: int = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = db.relationship(
        "Users",
        backref=db.backref("scheduled_execution", lazy=True),
    )

    exec_id: int = db.Column(db.Integer, db.ForeignKey("executions.id"))
    exec = db.relationship(
        "Executions",
        backref=db.backref("scheduled_execution", lazy=True),
    )

    def __repr__(self) -> str:  # pragma: no cover
        """Return the string representation of the scheduled job.

        Returns:
            str: String representation of the scheduled job.

        """
        return f"<Schedule {self.name}>"


class CrontabModel(db.Model):
    """Represents a crontab configuration for scheduling.

    Attributes:
        id (int): Primary key for the crontab entry.
        hour (str): Hour at which to run the job.
        minute (str): Minute at which to run the job.
        day_of_week (str): Day of the week for the job.
        day_of_month (str): Day of the month for the job.
        month_of_year (str): Month of the year for the job.

    """

    id = db.Column(db.Integer, primary_key=True)
    hour = db.Column(db.String(64), default="*")
    minute = db.Column(db.String(64), default="*")
    day_of_week = db.Column(db.String(64), default="*")
    day_of_month = db.Column(db.String(64), default="*")
    month_of_year = db.Column(db.String(64), default="*")

    def __init__(
        self,
        minute: str = "*",
        hour: str = "*",
        day_of_week: str = "*",
        day_of_month: str = "*",
        month_of_year: str = "*",
        *args: str | int,
        **kwargs: str | int,
    ) -> None:  # pragma: no cover
        """Initialize the crontab configuration with default or provided values.

        Args:
            minute (str): The minute to run the task.
            hour (str): The hour to run the task.
            day_of_week (str): The day of the week to run the task.
            day_of_month (str): The day of the month to run the task.
            month_of_year (str): The month of the year to run the task.
            *args (tuple[str | int]): Variable length argument list.
            **kwargs (dict[str, str | int]): Arbitrary keyword arguments.

        """
        self.minute = minute
        self.hour = hour
        self.day_of_week = day_of_week
        self.day_of_month = day_of_month
        self.month_of_year = month_of_year
