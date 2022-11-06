import argparse
import logging

from house_collector.data_collector import DataCollector

DB_HOST = "localhost"
DB_PORT = 27017


def main():
    """
    Main function
    """

    parser = argparse.ArgumentParser(
        description="Collects houses from different websites"
    )
    parser.add_argument(
        "-h",
        "--host",
        const=DB_HOST,
        default=DB_HOST,
        type=str,
        help="Database host",
    )
    parser.add_argument(
        "-p",
        "--port",
        const=DB_PORT,
        default=DB_PORT,
        type=int,
        help="Database port",
    )
    parser.add_argument(
        "-m",
        "--multi_thread",
        type=bool,
        const=True,
        default=False,
        help="Whether to allow multi-threading",
    )
    parser.add_argument(
        "-n",
        "--num_max_threads",
        const=100,
        default=100,
        type=int,
        help="Whether to allow multi-threading",
    )
    parser.add_argument(
        "-t",
        "--check_interval_min",
        const=30,
        default=30,
        type=int,
        help="Time to wait, in minutes, between checks",
    )
    parser.add_argument(
        "--run_once",
        const=True,
        default=False,
        type=bool,
        help="Run the program once and exit",
    )
    parser.add_argument(
        "-d",
        "--debug",
        const=True,
        default=False,
        type=bool,
        help="Whether to print the debug logs",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        const=True,
        default=False,
        type=bool,
        help="Whether to print the logs to the console",
    )

    parsed_args = parser.parse_args()

    if parsed_args.verbose:
        logging.getLogger().addHandler(logging.StreamHandler())
    if parsed_args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    logging.debug("Parsed arguments: %s", parsed_args)

    collector = DataCollector(
        db_host=parsed_args.host,
        db_port=parsed_args.port,
        max_threads=parsed_args.num_max_threads,
        use_threading=parsed_args.multi_thread,
        check_interval_min=parsed_args.check_interval_min,
    )

    if parsed_args.run_once:
        collector.run_once()
    else:
        collector.run()


if __name__ == "__main__":
    main()
