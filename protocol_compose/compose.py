import datetime
from typing import Iterable, Optional

import yaml
from more_itertools import transpose
from pydantic import BaseModel


class Design(BaseModel):
    treatments: int
    repetitions: int


class Activity(BaseModel):
    name: str
    product: str


Timing = str | datetime.date


class Sample(BaseModel):
    name: str
    freq: int
    ref: str


class Measurement(BaseModel):
    name: str
    timings: Optional[list[Timing]]
    samples: Optional[list[Sample]]
    subsamples: int = 1


class Protocol(BaseModel):
    design: Design
    activities: list[Activity]
    measurements: list[Measurement]

    @property
    def plots(self):
        return self.design.treatments * self.design.repetitions


def parse_timings(timings: list[Timing] | Timing | dict[str, int]) -> list[Timing]:
    match timings:
        case [*names]:
            valid = (len(names) <= 200) and names
            if not valid:
                raise ValueError(
                    "length of list of timings must be less than 200 and greater than 0"
                )
            return [n if isinstance(n, datetime.date) else str(n) for n in names]
        case {"step": int(step), "start": int(start), "until": int(until)}:
            valid = all((n <= 200) and (n >= 0) for n in [step, start, until])
            if not valid:
                raise ValueError(
                    "step, start and until timings parameters must be less than 200 and greater than 0"
                )
            return [str(n) for n in range(start, until + 1, step)]
        case datetime.date() as name:
            return [name]
        case str(name):
            return [name]
        case _:
            raise ValueError("timings not defined correctly")


def pluck_sample_tups(samples: Iterable[tuple[str, str]]) -> tuple[str, int, str]:
    for sname, freq_ref_str in samples:
        freq, ref = freq_ref_str.split("/")
        freq = int(freq)
        if (freq > 200) or (freq <= 0):
            raise ValueError("freq must be less than 200 and greater than 0")
        elif ref != "plot":
            raise NotImplementedError("sample references other than plot not yet implemented")
        yield sname, freq, ref


def parse_samples(samples: dict[str, str] | str) -> list[Sample]:
    if isinstance(samples, str):
        samples = {"": samples}
    elif not isinstance(samples, dict):
        raise ValueError("samples must be either a string or a dict (named sample)")
    elif len(samples) > 200:
        raise ValueError("there can be at most 200 named samples")
    sample_tuples = list(pluck_sample_tups(samples.items()))
    _, _, refs = transpose(sample_tuples)
    if len(set(refs)) > 1:
        raise NotImplementedError("heterogeneous sample references not supported")
    elif list(set(refs))[0] == "":
        raise ValueError("sample reference must not be null")
    return [Sample(name=n, freq=f, ref=r) for n, f, r in sample_tuples]


def parse_measurements(measurements: dict) -> list[Measurement] | None:
    parsed_measurements = []
    for name, measurement in measurements.items():
        timings = parse_timings(measurement["timings"])
        samples = parse_samples(measurement["samples"])
        if measurement.get("subsamples"):
            subsamples = measurement.get("subsamples")
        else:
            subsamples = 1
        parsed_measurements.append(
            Measurement(
                name=name,
                timings=timings,
                samples=samples,
                subsamples=subsamples,
            )
        )
    if parsed_measurements:
        return parsed_measurements
    return None


def parse_activities(activities: dict) -> list[Activity] | None:
    if activities:
        return [Activity(name=k, **v) for k, v in activities.items()]
    return None


def read_compose(filepath: str) -> Protocol:
    with open(filepath, "r") as f:
        protocolo_spec = yaml.safe_load(f)

    protocol: dict = protocolo_spec["protocol"]
    design: dict = protocol["design"]
    activities: dict = protocol["activities"]
    measurements: dict = protocol["measurements"]

    return Protocol(
        design=Design(**design),
        activities=parse_activities(activities),
        measurements=parse_measurements(measurements),
    )
