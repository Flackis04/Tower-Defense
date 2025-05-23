import os
import io
import tokenize

def remove_comments_from_source(source):
    io_obj = io.StringIO(source)
    tokens = list(tokenize.generate_tokens(io_obj.readline))
    tokens_without_comments = [token for token in tokens if token.type != tokenize.COMMENT]
    return tokenize.untokenize(tokens_without_comments)

def process_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        new_source = remove_comments_from_source(source)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_source)
        print(f"Processed: {file_path}")
    except Exception as e:
        print(f"Failed processing {file_path}: {e}")

if __name__ == "__main__":
    for root, dirs, files in os.walk('.'):
        for name in files:
            if name.endswith('.py'):
                full_path = os.path.join(root, name)
                process_file(full_path)