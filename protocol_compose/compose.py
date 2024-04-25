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


def read_compose(filepath: str) -> Protocol:
    with open(filepath, "r") as f:
        protocolo_spec = yaml.safe_load(f)

    protocol: dict = protocolo_spec["protocol"]
    activities: dict = protocolo_spec["activities"]
    measurements: dict = protocolo_spec["measurements"]

    if not all(map(lambda k: k in protocol["activities"], activities.keys())):
        raise KeyError("Activities not defined in protocol")
    elif not all(map(lambda k: k in protocol["measurements"], measurements.keys())):
        raise KeyError("Measurements not defined in protocol")

    return Protocol(
        design=Design(**protocol["design"]),
        activities=list(starmap(lambda k, a: Activity(name=k, **a), activities.items())),
        measurements=list(starmap(lambda k, m: Measurement(name=k, **m), measurements.items())),
    )
