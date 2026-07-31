import pysrt

def generate_srt(segments: list, output_path: str):
    """
    Takes a list of Whisper segments and saves them as an .srt subtitle file.
    """
    print(f"Generating subtitle file at {output_path}...")

    #Create an empty subtitle file object
    subs = pysrt.SubRipFile()

    for i, segment in enumerate(segments):
        # pysrt needs the time formatted into hours, minutes, seconds, milliseconds.
        # Whisper just gives us the total seconds (e.g. 65.5 seconds).
        # Use pysrt.SubRipTime.from_ordinal() which takes the total milliseconds to do the math for us

        start_ms = int(segment['start'] * 1000)
        end_ms = int(segment['end'] * 1000)

        start_time = pysrt.SubRipTime.from_ordinal(start_ms)
        end_time = pysrt.SubRipTime.from_ordinal(end_ms)

        # Create a single subtitle block (index, start time, end time, and text)
        # Note: Subtitle indexes always start at 1 and not 0

        sub_item = pysrt.SubRipItem(index = i + 1,
                                    start = start_time,
                                    end = end_time,
                                    text = segment['text'].strip() #.strip() removes any accidental spaces at the start/end
                                    )

        # Add the block to our file
        subs.append(sub_item)

    # Save the file to the hard drive
    subs.save(output_path, encoding = 'utf-8')
    print("Success! Subitiles generated.")

# --- Testing Block ---
if __name__ == "__main__":
    # Create some fake AI output to test it
    fake_whisper_output = [{'start': 0.0, 'end': 2.5, 'text': 'Welcome to my first Python project!'}, {'start': 2.5, 'end': 5.0, 'text': ' Today we are generating subtitles.'}]

    output_file = "test_subtitles.srt"

    generate_srt(fake_whisper_output, output_file)

    