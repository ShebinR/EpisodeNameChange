import json
import os
import re
import time

def changeName(location, current, new):
    file_current = location + "/" + current
    file_new = location + "/" + new
    print "Renaming : " + new
    time.sleep(0.25)
    os.rename(file_current, file_new)

season = 8
series_name = "The Big Bang Theory"
my_mapping = {}
my_real_file_names = []
f = open("list_of_episodes_Season_8.txt", "r")
for line in f:
        my_real_file_names.append(line)
f.close()

#print my_real_file_names
#location = "/home/shebin/Project/Episode_Name_Change/Sample_Data/The.Big.Bang.Theory.S04.Season.4.720p.5.1Ch.BluRay.ReEnc-DeeJayAhmed"
#location = "/mnt/Shebin_HD/Series/The.Big.Bang.Theroy/The.Big.Bang.Theory.S04.Season.4.720p.5.1Ch.BluRay.ReEnc-DeeJayAhmed"
#location = "/mnt/Shebin_HD/Series/The.Big.Bang.Theroy/The.Big.Bang.Theory.S05"
#location = "/mnt/Shebin_HD/Series/The.Big.Bang.Theroy/The.Big.Bang.Theory.S03"
location = "/mnt/Shebin_HD/Movies/English.Series/The.Big.Bang.Theroy/The.Big.Bang.Theory.S08"
actual_files = os.listdir(location)

for filename in my_real_file_names:
        fields = filename.split(" ", 1)
        if len(fields) < 2:
            continue
        #print fields
        episode = "S0" + str(season) + "E"
        if int(fields[0]) < 10:
            episode_number = "0" + str(fields[0])
        else:
            episode_number = str(fields[0])
        episode = episode + episode_number
        actual_name = series_name + "-" + episode
        actual_name = actual_name + "-" + fields[1]
        actual_name = actual_name.replace("\n", "").replace("\r", "").replace(" ", ".").replace("\/",".")
        print episode
        for files in actual_files:
#            exp = "01x" + episode_number
#            print exp
#            exp = "S07E" + episode_number
#            print exp
            if re.search(episode, files):
                extension = os.path.splitext(files)[1]
                if extension == ".srt":
                    srt_file = []
                    srt_file.append(files)
                    new_file = actual_name + ".srt"
                    srt_file.append(new_file)
                else:
                    media_file = []
                    media_file.append(files)
                    new_file = actual_name + ".mkv"
                    media_file.append(new_file)
        changeName(location, srt_file[0], srt_file[1])
        changeName(location, media_file[0], media_file[1])
        data = [episode, actual_name, srt_file, media_file]
        my_mapping[fields[0]] = data

print(json.dumps(my_mapping, indent = 4))
#print actual_files

