import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

# What to search for? KJP in this example to find out all occurances for Kouvolan JalkaPallo (KJP)
searchString = "KJP"

# Take the vakiovuorot PDF file that City of Kouvola provides, ctrl+a and then ctrl+c to copy to clipboard.
# Then paste as PLAIN TEXT and save to 'vakiovuorot_dump.txt', which will then be parsed by this script.
try:
    with open('vakiovuorot_dump.txt') as file:
        lines = file.readlines()
except FileNotFoundError:
    print("Error: vakiovuorot_dump.txt file not found")
    sys.exit(1)
except IOError:
    print("Error: Could not read vakiovuorot_dump.txt")
    sys.exit(1)

# weekdays as in MA/TI/KE/TO/PE/LA/SU (Monday/Tuesday/Wednesday/Thursday/Friday/Saturday/Sunday), initialize to None and change during for loop.
weekday = None
# Site as in "Kohde" in the original, initialize to None and change during for loop.
site = None

# Print the header of the CSV file, where SEMICOLON is separator.
print("Tila;viikonpäivä;Tilatarkennus;Klo;Ryhmä;Aikaväli")

# Go through the dump line by line...
for i in range(len(lines)):
    
    # Pages start with Kohde, store that as site first
    if "Kohde:" in lines[i]:
        site = str(re.sub('\n', '', lines[i+1]) + " - " + re.sub('\n', '', lines[i+2]))
        if "," in site:
            site = site.replace(",", "")

    # continue to parse the page by looking at weekdays    
    elif "MA\n" in lines[i] or "TI\n" in lines[i] or "KE\n" in lines[i] or "TO\n" in lines[i] or "PE\n" in lines[i] or "LA\n" in lines[i] or "SU\n" in lines[i]:
        weekday = str(re.sub('\n', '', lines[i]))

    # and finally see if there are matches to your search-string
    elif searchString in lines[i]:
        # check if there is "tilatarkennus" or no... because the formatting is different if there is.
        if ".2024" in lines[i-2] or ".2025" in lines[i-2] or ".2026" in lines[i-2] or "MA\n" in lines[i-2] or "TI\n" in lines[i-2] or "KE\n" in lines[i-2] or "TO\n" in lines[i-2] or "PE\n" in lines[i-2] or "LA\n" in lines[i-2] or "SU\n" in lines[i-2]:
            print(site.encode('ansi').decode('utf-8') + ";" + weekday + ";ei-tilatarkennusta;" + re.sub('\n', '', lines[i-1]) + ";" + re.sub('\n', '', lines[i]) + ";" + re.sub('\n', '', lines[i+1]))
        else:
            print(site.encode('ansi').decode('utf-8') + ";" + weekday + ";" + re.sub('\n', '', lines[i-2].encode('ansi').decode('utf-8')) + ";" + re.sub('\n', '', lines[i-1]) + ";" + re.sub('\n', '', lines[i]) + ";" + re.sub('\n', '', lines[i+1]))

# At the end, you should have SEMICOLON separated format output in your terminal/console, that you can then copy paste to spreadsheet tool you like, i.e. Microsoft Excel.
