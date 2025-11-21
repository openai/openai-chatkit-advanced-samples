"""ProfileCard widget generator agent."""

from typing import Any

from agents import Agent
from pydantic import BaseModel, Field


class Origin(BaseModel):
    """Origin location details."""

    city: str
    state: str
    country: str


class AstrologicalNotes(BaseModel):
    """Astrological sign information."""

    sun_sign: str
    moon_sign: str
    venus_sign: str
    mars_sign: str


class ProfileCardOutput(BaseModel):
    """Output schema for ProfileCard widget."""

    name: str
    age: int
    occupation: str
    location: str
    birthdate: str
    origin: Origin
    astrological_notes: AstrologicalNotes
    short_bio: str


INSTRUCTIONS = """You are a ProfileCard generator agent. Your job is to transform character YAML data into a structured ProfileCard widget format.

Given character data, extract and format the following fields:
- name
- age
- occupation
- location
- birthdate
- origin (city, state, country)
- astrological_notes (sun_sign, moon_sign, venus_sign, mars_sign)
- short_bio

Ensure all astrological signs are in UPPERCASE (e.g., ARIES, VIRGO, TAURUS).
Use the existing data as-is without modification."""


profilecard_agent = Agent[None](
    model="gpt-5.1",
    name="ProfileCard Generator",
    instructions=INSTRUCTIONS,
    output_type=ProfileCardOutput,
)
