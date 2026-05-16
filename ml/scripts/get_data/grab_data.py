import asyncio

from scripts.get_data.get_fundamentals import main as get_fundamentals
from scripts.get_data.get_price_history import main as get_price_history
from scripts.get_data.get_snp_500 import main as get_snp_500


async def _price_and_fundamentals_async_runner():
    """Run the price history and fundamentals download concurretly.

    Delegates each download to a separate thread so they execute in parallel without
    blocking the event loop.
    """
    async with asyncio.TaskGroup() as tg:
        tg.create_task(asyncio.to_thread(get_fundamentals))
        tg.create_task(asyncio.to_thread(get_price_history))


def main():
    """Orchestrate the full data retrievval pipeline.

    First fetches the S&P 500 constituents list, then downloads price histories and
    fundamentals metrics concurrently.
    """
    print("Retrieving S&P 500 constituents...")
    get_snp_500()
    print("...S&P retrieved.")

    print("Retrieving price histories and fundamentals for S&P 500 constituents...")
    asyncio.run(_price_and_fundamentals_async_runner())
    print("...Price histories and fundamentals retrieved.")


if __name__ == "__main__":
    main()
