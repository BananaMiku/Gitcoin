#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "sha1.h"

void print_digest(unsigned char hash[20]) {
    for(int i = 0; i < 20; i++) {
        fprintf(stderr, "%02x", hash[i]);
    }
    printf("\n");
}

typedef struct nonce {
    unsigned char data[16];
} nonce;

typedef struct nonce_iterable {
    uint64_t l;
    uint64_t h;
} nonce_iterable;

char *hex_chars = "0123456789abcdef";

void mine_single(nonce new_nonce, char *block, uint32_t length, unsigned char hash[20]) {
    char *nonce_location = block + length - 33;
    for(int i = 0; i < 16; i++) {
        nonce_location[30 - i * 2] = hex_chars[(new_nonce.data[i] & 0xf0) >> 4];
        nonce_location[31 - i * 2] = hex_chars[new_nonce.data[i] & 0x0f];
    }
    char *header = block;
    char *data = block + 1 + strlen(header);
    fprintf(stderr, "===header===\n%s\n", header);
    fprintf(stderr, "===data===\n%s\n===sha1 hash===\n", data);

    SHA1(hash, block, length);

    print_digest(hash);
    fprintf(stderr, "\n");
}

static PyObject *mine(PyObject *self, PyObject *args)
{
    int x;
    if (!PyArg_ParseTuple(args, "i", &x))
        return NULL;
    return PyLong_FromLong(x * 2);
}

int main() {
    char my_string[1000];
    for(int i = 0; i < 1000; i++) {
        my_string[i] = 0;
    }
    char *head = my_string;
    while((head[0] = fgetc(stdin)) != EOF) {
        head++;
    }
    head[0] = 0;
    
    uint32_t length = strlen(my_string);
    char *data_block = my_string + strlen(my_string) + 1;
    length += strlen(data_block) + 1;

    unsigned char hash_out[20];
    SHA1(hash_out, my_string, length);

    print_digest(hash_out);

    fprintf(stderr, "Mining with template: \n");
    fprintf(stderr, "===header===\n%s\n", my_string);
    fprintf(stderr, "===data===\n%s\n===data===\n", data_block);

    unsigned char hash[20];
    uint64_t i = 0;
    while(hash[0] || hash[1]) {
        nonce_iterable my_nonce;
        my_nonce.l = i;
        my_nonce.h = 0;
        mine_single(*((nonce *)&my_nonce), my_string, length, hash);
        i++;
    }
    printf("%s\n", data_block);
}
