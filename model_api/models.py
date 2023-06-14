from pydantic import BaseModel


class ExpectedInputPrepped(BaseModel):
    temperature_2m_mean: float = 18.4
    temperature_2m_min: float = 11.4
    temperature_2m_max: float = 25.4
    rain_sum: float = 3.2

