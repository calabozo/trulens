import asyncio
import unittest

from opentelemetry import trace
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)
import pandas as pd
from trulens.experimental.otel_tracing.core.instrument import _get_func_name
from trulens.experimental.otel_tracing.core.instrument import instrument
from trulens.experimental.otel_tracing.core.session import (
    _set_up_tracer_provider,
)


class TestOtelInstrument(unittest.TestCase):
    def setUp(self) -> None:
        # Set up OTEL tracing.
        self.exporter = InMemorySpanExporter()
        _set_up_tracer_provider()
        self.span_processor = SimpleSpanProcessor(self.exporter)
        trace.get_tracer_provider().add_span_processor(self.span_processor)
        return super().setUp()

    def tearDown(self) -> None:
        self.span_processor.shutdown()
        return super().tearDown()

    def test__get_func_name(self):
        self.assertEqual(
            _get_func_name(lambda: None),
            "tests.unit.test_otel_instrument.TestOtelInstrument.test__get_func_name.<locals>.<lambda>",
        )
        self.assertEqual(
            _get_func_name(self.test__get_func_name),
            "tests.unit.test_otel_instrument.TestOtelInstrument.test__get_func_name",
        )
        self.assertEqual(
            _get_func_name(pd.DataFrame.transpose),
            "pandas.core.frame.DataFrame.transpose",
        )

    def test_sync_non_generator_function(self):
        # Set up instrumented function.
        @instrument(
            attributes=lambda ret, exception, *args, **kwargs: {
                "best_baby": ret
            }
        )
        def my_function():
            return "Kojikun"

        # Run the function.
        my_function()
        # Verify that the span is emitted correctly.
        spans = self.exporter.get_finished_spans()
        self.assertEqual(len(spans), 1)
        self.assertEqual(
            spans[0].name,
            "tests.unit.test_otel_instrument.TestOtelInstrument.test_sync_non_generator_function.<locals>.my_function",
        )
        self.assertEqual(
            spans[0].attributes["trulens.unknown.best_baby"], "Kojikun"
        )

    # def test_sync_generator_function(self):
    #     # Set up instrumented function.
    #     @instrument(
    #         attributes=lambda ret, exception, *args, **kwargs: {
    #             "best_babies": ret
    #         }
    #     )
    #     def my_function():
    #         yield "Kojikun"
    #         yield "Nolan"
    #         yield "Sachiboy"
    #
    #     # Run the function.
    #     my_function()
    #     # Verify that the span is emitted correctly.
    #     spans = self.exporter.get_finished_spans()
    #     self.assertEqual(len(spans), 1)
    #     self.assertEqual(
    #         spans[0].name,
    #         "tests.unit.test_otel_instrument.TestOtelInstrument.test_sync_generator_function.<locals>.my_function",
    #     )
    #     self.assertListEqual(
    #         spans[0].attributes["trulens.unknown.best_babies"],
    #         ["Kojikun", "Nolan", "Sachiboy"],
    #     )

    def test_async_non_generator_function(self):
        # Set up instrumented function.
        @instrument(
            attributes=lambda ret, exception, *args, **kwargs: {
                "best_baby": ret
            }
        )
        async def my_function():
            await asyncio.sleep(0.00001)
            return "Kojikun"

        # Run the function.
        asyncio.run(my_function())
        # Verify that the span is emitted correctly.
        spans = self.exporter.get_finished_spans()
        self.assertEqual(len(spans), 1)
        self.assertEqual(
            spans[0].name,
            "tests.unit.test_otel_instrument.TestOtelInstrument.test_async_non_generator_function.<locals>.my_function",
        )
        self.assertEqual(
            spans[0].attributes["trulens.unknown.best_baby"], "Kojikun"
        )

    # def test_async_generator_function(self):
    #     # Set up instrumented function.
    #     @instrument(
    #         attributes=lambda ret, exception, *args, **kwargs: {
    #             "best_babies": ret
    #         }
    #     )
    #     async def my_function():
    #         await asyncio.sleep(0.00001)
    #         yield "Kojikun"
    #         yield "Nolan"
    #         yield "Sachiboy"
    #
    #     # Run the function.
    #     async def consume_async_generator(async_generator):
    #         async for curr in async_generator:
    #             print(f"\t{curr}")
    #
    #     asyncio.run(consume_async_generator(my_function()))
    #     # Verify that the span is emitted correctly.
    #     spans = self.exporter.get_finished_spans()
    #     self.assertEqual(len(spans), 1)
    #     self.assertEqual(
    #         spans[0].name,
    #         "tests.unit.test_otel_instrument.TestOtelInstrument.test_async_generator_function.<locals>.my_function",
    #     )
    #     self.assertListEqual(
    #         spans[0].attributes["trulens.unknown.best_babies"],
    #         ["Kojikun", "Nolan", "Sachiboy"],
    #     )


if __name__ == "__main__":
    unittest.main()
