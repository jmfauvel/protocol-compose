import datetime
from itertools import starmap
from typing import Optional

import rich
import yaml
from pydantic import BaseModel


class Design(BaseModel):
    treatments: int
    repetitions: int


class Activity(BaseModel):
    name: str
    product: str


class Measurement(BaseModel):
    name: str
    samples: str | list[str]
    timings: list[str] | list[datetime.date]
    start: Optional[str | int | datetime.date] = None
    until: Optional[str | int | datetime.date] = None
    subsamples: int = 1
    nullable: bool = False
    ordered: bool = True
    strict: bool = True


class Protocol(BaseModel):
    design: Design
    activities: list[Activity]
    measurements: list[Measurement]

    @property
    def plots(self):
        return self.design.treatments * self.design.repetitions


def read_compose(filepath: str) -> Protocol:
    with open(filepath, "r") as f:
        protocolo_spec = yaml.safe_load(f)

    protocol: dict = protocolo_spec["protocol"]
    activities: dict = protocolo_spec["activities"]
    measurements: dict = protocolo_spec["measurements"]

    # checking if all activities/measurements defined as a list[str] in
    # protocol["measurements"]/protocol["activities"] are also defined in activities/measurment
    if not all([k in protocol["activities"] for k in activities.keys()]):
        raise KeyError("Activities not defined in protocol")
    elif not all([k in protocol["measurements"] for k in measurements.keys()]):
        raise KeyError("Measurements not defined in protocol")

    return Protocol(
        design=Design(**protocol["design"]),
        activities=[Activity(name=k, **v) for k, v in activities.items()],
        measurements=[Measurement(name=k, **v) for k, v in measurements.items()],
    )
