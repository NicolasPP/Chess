MainTests()
{
  pytest tests/utils tests/chess
}

OnlyIntegrated()
{
  pytest tests/test_with_played_games.py
}

TestAll()
{
  pytest tests/utils tests/chess tests/test_with_played_games.py
}

InvalidOption()
{
	echo "------------ INVALID OPTION : [$1] ------------"
	ValidOptions
	exit 1
}

ValidOptions()
{
	echo "---------------- VALID OPTIONS ----------------"
	  echo "	-a | --all        : run all tests"
    echo "	-i | --integrated : run integrated tests only"
    echo "	-t | --type-check : run mypy check"
}

TypeCheck()
{
  mypy . --check-untyped-defs --explicit-package-bases
}


no_args="true"
while [ $# -gt 0 ] ; do
  case $1 in
    -a | --all) TestAll;;
    -i | --integrated) OnlyIntegrated ;;
    -t | --type-check) TypeCheck ;;
	*) InvalidOption $1;;

  esac
  no_args="false"
  shift
done

[[ "$no_args" == "true" ]] && { MainTests; exit 1; }