import dataclasses
import datetime
import itertools

from typing import Any, Dict, Iterable, List, Optional
from ._enum import InsightType

import dacite


@dataclasses.dataclass
class RawInsight:
    type: InsightType
    data: Dict[str, Any]
    value_tag: Optional[str] = None
    value: Optional[str] = None
    automatic_processing: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self, dict_factory=dict_factory)


@dataclasses.dataclass
class ProductInsights:
    insights: List[RawInsight]
    barcode: str
    type: InsightType
    source_image: Optional[str] = None

    @classmethod
    def merge(cls, items: Iterable["ProductInsights"]) -> "ProductInsights":
        items = list(items)
        if len(items) == 0:
            raise ValueError("no items to merge")

        elif len(items) == 1:
            return items[0]

        for field_name in ("type", "barcode", "source_image"):
            values = set(getattr(x, field_name) for x in items)
            if len(values) > 1:
                raise ValueError(
                    "more than one value for '{}': {}".format(field_name, values)
                )
        item = items[0]
        insights = list(
            itertools.chain.from_iterable((item.insights for item in items))
        )
        return cls(
            insights=insights,
            barcode=item.barcode,
            type=item.type,
            source_image=item.source_image,
        )

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self, dict_factory=dict_factory)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProductInsights":
        return dacite.from_dict(
            data_class=cls, data=data, config=dacite.Config(cast=[InsightType])
        )


@dataclasses.dataclass
class Insight:
    barcode: str
    type: InsightType
    data: Dict[str, Any]
    valid: bool
    value_tag: Optional[str] = None
    value: Optional[str] = None
    automatic_processing: Optional[bool] = None
    source_image: Optional[str] = None
    reserved_barcode: bool = False
    server_domain: str = ""
    server_type: str = ""
    id: str = ""
    timestamp: Optional[datetime.datetime] = None
    countries: List[str] = dataclasses.field(default_factory=list)
    brands: List[str] = dataclasses.field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self, dict_factory=dict_factory)

    @classmethod
    def from_raw_insight(
        cls, insight: RawInsight, product_insights: ProductInsights, valid: bool
    ) -> "Insight":
        type: InsightType
        return cls(
            valid=valid,
            type=insight.type,
            data=insight.data,
            value_tag=insight.value_tag,
            value=insight.value,
            automatic_processing=insight.automatic_processing,
            barcode=product_insights.barcode,
            source_image=product_insights.source_image,
        )


def dict_factory(*args, **kwargs):
    d = dict(*args, **kwargs)
    for key, value in d.items():
        if isinstance(value, InsightType):
            d[key] = value.name

    return d