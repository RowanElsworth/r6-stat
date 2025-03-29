
cleanup() {
  # Clean up
  echo "Cleaning up :)"
  rm -r "./$last_dir"
  # rm "./game.json"
}

# Ensures cleanup happens on exit (success and error)
trap cleanup EXIT

# Check Python is installed
# if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
#     echo "Python is not installed. Please install Python to continue."
#     exit 1
# fi

# if ! python -c "import xlsxwriter" &> /dev/null; then
#     echo "'xlsxwriter' is not installed. Installing now..."
#     python -m pip install xlsxwriter
# fi

# Take input
echo "Enter a number (1-12, latest-oldest) to get a folder path:"
read -r num

# Replace this with your replay dir
dir="C:/Program Files (x86)/Steam/steamapps/common/Tom Clancy's Rainbow Six Siege/MatchReplay/"

selected_folder=$(ls -d "$dir"*/ | sort -r | sed -n "${num}p")

if [[ -n "$selected_folder" ]]; then
    echo "Selected folder: $selected_folder"
else
    echo "Invalid selection or no folders found."
fi

# Copies folder locally
echo "Copying folder locally."
cp -r "$selected_folder" ./

last_dir=$(basename "$selected_folder")

# Run dissect application
echo "Converting video to statistics."
./dependencies/r6-dissect "./$last_dir" -o game.json
if [ $? -ne 0 ]; then
    echo "Error running r6-dissect. You should probably cry now :'(."
    exit 1
fi

# Convert the JSON output to XLSX
echo "Outputting statistics as XLSX spreadsheet"
py ./dependencies/ReplayAnalyzer.py
if [ $? -ne 0 ]; then
    echo "Error running ReplayAnalyzer.py. You should probably cry now :'(."
    exit 1
fi

echo "Spreadsheet is in ./Output"