def read_text_file(filename: str):
    with open(filename, 'rb') as f:
        try:
            data = f.read().decode('windows-1252')
            return data
        except:
            pass

        try:
            data = f.read().decode('utf-8')
            return data
        except:
            return ""

