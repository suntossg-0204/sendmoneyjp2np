import subprocess
import sys


def run(command):
    subprocess.run(command, shell=True)


def menu():
    while True:
        print()
        print("=" * 50)
        print(" RemitTracker JP Developer Toolkit")
        print("=" * 50)
        print("1. Run full pipeline")
        print("2. Inspect SBI Remit")
        print("3. Test Wise collector")
        print("4. Test Panda collector")
        print("5. Export JSON only")
        print("6. Git status")
        print("0. Exit")
        print("=" * 50)

        choice = input("Select: ").strip()

        if choice == "1":
            run("python scripts/run_pipeline.py")

        elif choice == "2":
            run("python scripts/helpers/inspect_sbi.py")

        elif choice == "3":
            run("python scripts/collectors/wise.py")

        elif choice == "4":
            run("python scripts/collectors/panda_api.py")

        elif choice == "5":
            run("python scripts/core/exporter.py")

        elif choice == "6":
            run("git status")

        elif choice == "0":
            print("Bye.")
            sys.exit()

        else:
            print("Invalid option.")


if __name__ == "__main__":
    menu()