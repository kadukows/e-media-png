from libs.png_decode import decode, PNG_HEADER

def main():
    with open('lena.png', 'rb') as file:
        chunks = decode(file)

        for chunk in chunks:
            print(chunk)


        mandatory_chunks = (chunk for chunk in chunks if chunk.chunk_name[0].isupper())
        with open('lena_new.png', 'wb') as out_file:
            out_file.write(PNG_HEADER)
            for chunk in mandatory_chunks:
                print(f'writing chunk: {chunk}')
                out_file.write(chunk.to_bytes())



if __name__ == '__main__':
    main()
