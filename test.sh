MainTests()
{
  pytest tests/chess
}

OnlyPlayedGames()
{
  pytest -v -m played_games
}

TestAll()
{
  pytest tests/chess tests/test_with_played_games.py
  TypeCheck
  ShowCovBrowser
}

ShowCovBrowser()
{
  open htmlcov/index.html
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
    echo "	-p | --played-games : test already played games"
    echo "	-t | --type-check : run mypy check"
}

TypeCheck()
{
  mypy src/ --check-untyped-defs
}


no_args="true"
while [ $# -gt 0 ] ; do
  case $1 in
    -a | --all) TestAll ;;
    -p | --played-games) OnlyPlayedGames ;;
    -t | --type-check) TypeCheck ;;
	*) InvalidOption $1 ;;

  esac
  no_args="false"
  shift
done

[[ "$no_args" == "true" ]] && { MainTests; exit 1; }