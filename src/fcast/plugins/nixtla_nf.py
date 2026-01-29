from __future__ import annotations
# Optional: requires `pip install -e .[nixtla]`
# This file is intentionally lightweight and safe to import without neuralforecast installed.
from fcast.plugins.base import LibraryAdapter, ApiSymbol, ApiParam

class NeuralForecastAdapter(LibraryAdapter):
    def library_name(self) -> str:
        return "neuralforecast"

    def extract_symbols(self) -> list[ApiSymbol]:
        # Minimal static example: use docs to seed; real extraction can use inspect.signature when installed.
        return [
            ApiSymbol(
                qualname="neuralforecast.core.NeuralForecast.fit",
                kind="method",
                signature="fit(df=None, static_df=None, val_size=0, ...)",
                params=[
                    ApiParam(name="df", type_repr="DataFrame|SparkDF|None"),
                    ApiParam(name="static_df", type_repr="DataFrame|None"),
                    ApiParam(name="val_size", type_repr="int", default_repr="0"),
                ],
                doc_url="https://nixtlaverse.nixtla.io/neuralforecast/core.html",
            )
        ]
