#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdbool.h>
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

/**
 * Mines a single nonce
 */
bool mine_single_fast(SHA1_CTX ctx, nonce nonce, char *nonce_string) {
    char hash[20];
    for(int i = 0; i < 16; i++) {
        nonce_string[30 - i * 2] = hex_chars[(nonce.data[i] & 0xf0) >> 4];
        nonce_string[31 - i * 2] = hex_chars[nonce.data[i] & 0x0f];
    }

    for(int i = 0; i < 33; i++) {
        SHA1Update(&ctx, (const unsigned char*)nonce_string + i, 1);
    }
    SHA1Final((unsigned char *)hash, &ctx);

    return hash[0] || hash[1] || hash[2] || (hash[3] & 0xf0);
}

static PyObject *mine(PyObject *self, PyObject *args)
{
    Py_buffer block;
    if (!PyArg_ParseTuple(args, "y*", &block))
        return NULL;

    uint64_t hash_value = 0;
    
    SHA1_CTX ctx;
    SHA1Init(&ctx);
    for (int i = 0; i < block.len - 33; i++)
        SHA1Update(&ctx, (const unsigned char*)block.buf + i, 1);

    nonce_iterable my_nonce;
    do {
        hash_value++;
        my_nonce.l = hash_value;
        my_nonce.h = 0;
    } while (mine_single_fast(ctx, *((nonce *)&my_nonce), block.buf + block.len - 33));

    return PyBytes_FromStringAndSize(block.buf, block.len);
}

static PyMethodDef methods[] = {
    {"mine", mine, METH_VARARGS, "mining"},
    {NULL, NULL, 0, NULL} // Sentinel
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "mine_cpu",
    NULL,
    -1,
    methods
};

PyMODINIT_FUNC
PyInit_mine_cpu(void)
{
    return PyModule_Create(&module);
}

