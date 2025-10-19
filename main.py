import argparse, json

from homework_tools import HomeworkTools as HT

if __name__ == "__main__":
    commands = ["plagiarism:extract", "plagiarism:check", "session:group","testbench:extract"]

    parser = argparse.ArgumentParser(description="General tools for TAs.")
    parser.add_argument("-c","--config", default="config.json", help="Config file to define variables", metavar="filepath")
    parser.add_argument("command", choices=commands, help="Command to run")
    args = parser.parse_args()

    try:
        with open(args.config, "r", encoding="utf-8") as fp:
            config = json.load(fp)

        ht = HT(config)

        if args.command == "plagiarism:extract":
            ht.plagiarism_extract()
        elif args.command == "testbench:extract":
            ht.testbench_extract()
        elif args.command == "plagiarism:check":
            ht.plagiarism_check()
        elif args.command == "session:group":
            ht.session_create()
        else:
            raise RuntimeError(f"Unimplemented command: \"{args.command}\"")
    except RuntimeError as e:
        print(e)
