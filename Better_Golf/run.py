"""Better_Golf CLI.

  python run.py solve <n>            solve one task, log, report
  python run.py sweep <a> <b>        solve tasks a..b, refresh logs
  python run.py render               regenerate TASK_INDEX.md / SOLVE_LOG.md
  python run.py package              build out/submission.zip
  python run.py submit "<msg>" [--force]
"""
import sys

from engine import package, solve


def main(argv):
    if not argv:
        print(__doc__)
        return
    cmd = argv[0]
    if cmd == "solve":
        r = solve.solve_one(int(argv[1]))
        print(f"task{int(argv[1]):03d}: {r['status']} | "
              f"{r['family']} | {r['points']} pts | note: {r['note']}")
    elif cmd == "sweep":
        solve.sweep(int(argv[1]), int(argv[2]))
    elif cmd == "render":
        solve.render_all()
        print("regenerated logs/TASK_INDEX.md and logs/SOLVE_LOG.md")
    elif cmd == "package":
        print("built", package.build_zip())
    elif cmd == "submit":
        print(package.submit(argv[1], force="--force" in argv))
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
