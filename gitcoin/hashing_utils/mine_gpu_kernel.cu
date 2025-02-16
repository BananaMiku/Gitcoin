#include <iostream>

/*
Based on
SHA-1 in C
By Steve Reid <steve@edmweb.com>
100% Public Domain

Test Vectors (from FIPS PUB 180-1)
"abc"
  A9993E36 4706816A BA3E2571 7850C26C 9CD0D89D
"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq"
  84983E44 1C3BD26E BAAE4AA1 F95129E5 E54670F1
A million repetitions of "a"
  34AA973C D4C4DAA4 F61EEB2B DBAD2731 6534016F
*/

#include <string.h>

#include <cstdint>

#include "sha1.h"


#define rol(value, bits) (((value) << (bits)) | ((value) >> (32 - (bits))))

/* blk0() and blk() perform the initial expand. */
/* I got the idea of expanding during the round function from SSLeay */
#define blk0(i) (block->l[i] = (rol(block->l[i],24)&0xFF00FF00) \
    |(rol(block->l[i],8)&0x00FF00FF))

#define blk(i) (block->l[i&15] = rol(block->l[(i+13)&15]^block->l[(i+8)&15] \
    ^block->l[(i+2)&15]^block->l[i&15],1))

/* (R0+R1), R2, R3, R4 are the different operations used in SHA1 */
#define R0(v,w,x,y,z,i) z+=((w&(x^y))^y)+blk0(i)+0x5A827999+rol(v,5);w=rol(w,30);
#define R1(v,w,x,y,z,i) z+=((w&(x^y))^y)+blk(i)+0x5A827999+rol(v,5);w=rol(w,30);
#define R2(v,w,x,y,z,i) z+=(w^x^y)+blk(i)+0x6ED9EBA1+rol(v,5);w=rol(w,30);
#define R3(v,w,x,y,z,i) z+=(((w|x)&y)|(w&x))+blk(i)+0x8F1BBCDC+rol(v,5);w=rol(w,30);
#define R4(v,w,x,y,z,i) z+=(w^x^y)+blk(i)+0xCA62C1D6+rol(v,5);w=rol(w,30);


/* Hash a single 512-bit block. This is the core of the algorithm. */

class SHA1_CTX {
public:
    uint32_t state[5];
    uint32_t count[2];
    unsigned char buffer[64];

    __device__ __host__
    SHA1_CTX() {
        state[0] = 0x67452301;
        state[1] = 0xEFCDAB89;
        state[2] = 0x98BADCFE;
        state[3] = 0x10325476;
        state[4] = 0xC3D2E1F0;
        count[0] = count[1] = 0;
    }

    __device__ __host__
    void update(const unsigned char *data, uint32_t len) {
        uint32_t i;

        uint32_t j;

        j = count[0];
        if ((count[0] += len << 3) < j)
            count[1]++;
        count[1] += (len >> 29);
        j = (j >> 3) & 63;
        if ((j + len) > 63)
        {
            memcpy(&buffer[j], data, (i = 64 - j));
            SHA1Transform(state, buffer);
            for (; i + 63 < len; i += 64)
            {
                SHA1Transform(state, &data[i]);
            }
            j = 0;
        }
        else
            i = 0;
        memcpy(&buffer[j], &data[i], len - i);
    }

    __device__ __host__
    void final(unsigned char digest[20]) {
        unsigned i;

        unsigned char finalcount[8];

        unsigned char c;

        for (i = 0; i < 8; i++)
        {
            finalcount[i] = (unsigned char) ((count[(i >= 4 ? 0 : 1)] >> ((3 - (i & 3)) * 8)) & 255);      /* Endian independent */
        }
        c = 0200;
        update(&c, 1);
        while ((count[0] & 504) != 448)
        {
            c = 0000;
            update(&c, 1);
        }
        update(finalcount, 8); /* Should cause a SHA1Transform() */
        for (i = 0; i < 20; i++)
        {
            digest[i] = (unsigned char)
                ((state[i >> 2] >> ((3 - (i & 3)) * 8)) & 255);
        }
    }
};

struct Nonce {
    unsigned char data[16];
};

__device__ __host__
void SHA1Transform(
    uint32_t state[5],
    const unsigned char buffer[64]
)
{
    uint32_t a, b, c, d, e;

    typedef union
    {
        unsigned char c[64];
        uint32_t l[16];
    } CHAR64LONG16;

    CHAR64LONG16 block[1];      /* use array to appear as a pointer */

    memcpy(block, buffer, 64);

    /* Copy context->state[] to working vars */
    a = state[0];
    b = state[1];
    c = state[2];
    d = state[3];
    e = state[4];
    /* 4 rounds of 20 operations each. Loop unrolled. */
    R0(a, b, c, d, e, 0);
    R0(e, a, b, c, d, 1);
    R0(d, e, a, b, c, 2);
    R0(c, d, e, a, b, 3);
    R0(b, c, d, e, a, 4);
    R0(a, b, c, d, e, 5);
    R0(e, a, b, c, d, 6);
    R0(d, e, a, b, c, 7);
    R0(c, d, e, a, b, 8);
    R0(b, c, d, e, a, 9);
    R0(a, b, c, d, e, 10);
    R0(e, a, b, c, d, 11);
    R0(d, e, a, b, c, 12);
    R0(c, d, e, a, b, 13);
    R0(b, c, d, e, a, 14);
    R0(a, b, c, d, e, 15);
    R1(e, a, b, c, d, 16);
    R1(d, e, a, b, c, 17);
    R1(c, d, e, a, b, 18);
    R1(b, c, d, e, a, 19);
    R2(a, b, c, d, e, 20);
    R2(e, a, b, c, d, 21);
    R2(d, e, a, b, c, 22);
    R2(c, d, e, a, b, 23);
    R2(b, c, d, e, a, 24);
    R2(a, b, c, d, e, 25);
    R2(e, a, b, c, d, 26);
    R2(d, e, a, b, c, 27);
    R2(c, d, e, a, b, 28);
    R2(b, c, d, e, a, 29);
    R2(a, b, c, d, e, 30);
    R2(e, a, b, c, d, 31);
    R2(d, e, a, b, c, 32);
    R2(c, d, e, a, b, 33);
    R2(b, c, d, e, a, 34);
    R2(a, b, c, d, e, 35);
    R2(e, a, b, c, d, 36);
    R2(d, e, a, b, c, 37);
    R2(c, d, e, a, b, 38);
    R2(b, c, d, e, a, 39);
    R3(a, b, c, d, e, 40);
    R3(e, a, b, c, d, 41);
    R3(d, e, a, b, c, 42);
    R3(c, d, e, a, b, 43);
    R3(b, c, d, e, a, 44);
    R3(a, b, c, d, e, 45);
    R3(e, a, b, c, d, 46);
    R3(d, e, a, b, c, 47);
    R3(c, d, e, a, b, 48);
    R3(b, c, d, e, a, 49);
    R3(a, b, c, d, e, 50);
    R3(e, a, b, c, d, 51);
    R3(d, e, a, b, c, 52);
    R3(c, d, e, a, b, 53);
    R3(b, c, d, e, a, 54);
    R3(a, b, c, d, e, 55);
    R3(e, a, b, c, d, 56);
    R3(d, e, a, b, c, 57);
    R3(c, d, e, a, b, 58);
    R3(b, c, d, e, a, 59);
    R4(a, b, c, d, e, 60);
    R4(e, a, b, c, d, 61);
    R4(d, e, a, b, c, 62);
    R4(c, d, e, a, b, 63);
    R4(b, c, d, e, a, 64);
    R4(a, b, c, d, e, 65);
    R4(e, a, b, c, d, 66);
    R4(d, e, a, b, c, 67);
    R4(c, d, e, a, b, 68);
    R4(b, c, d, e, a, 69);
    R4(a, b, c, d, e, 70);
    R4(e, a, b, c, d, 71);
    R4(d, e, a, b, c, 72);
    R4(c, d, e, a, b, 73);
    R4(b, c, d, e, a, 74);
    R4(a, b, c, d, e, 75);
    R4(e, a, b, c, d, 76);
    R4(d, e, a, b, c, 77);
    R4(c, d, e, a, b, 78);
    R4(b, c, d, e, a, 79);
    /* Add the working vars back into context.state[] */
    state[0] += a;
    state[1] += b;
    state[2] += c;
    state[3] += d;
    state[4] += e;
    /* Wipe variables */
    a = b = c = d = e = 0;
    memset(block, '\0', sizeof(block));
}



/* Add padding and return the message digest. */

__device__ __host__
void SHA1(
    char *hash_out,
    const char *str,
    uint32_t len)
{
    SHA1_CTX ctx;
    unsigned int ii;

    for (ii=0; ii<len; ii+=1)
        ctx.update((const unsigned char*)str + ii, 1);
    ctx.final((unsigned char *)hash_out);
}

__device__ __host__
bool mine_single_fast(SHA1_CTX ctx, Nonce nonce) {
    char nonce_string[20];
    char hash[20];
    for(int i = 0; i < 16; i++) {
        nonce_string[30 - i * 2] = hex_chars[(nonce.data[i] & 0xf0) >> 4];
        nonce_string[31 - i * 2] = hex_chars[nonce.data[i] & 0x0f];
    }

    for(int i = 0; i < 33; i++) {
        ctx.update((const unsigned char*)nonce_string + i, 1);
    }
    ctx.final((unsigned char *)hash);

    return hash[0] || hash[1];
}

constexpr size_t THREADS_PER_BLOCK = 32;

__global__ 
void mine(SHA1_CTX original, Nonce *target, size_t limit) {
    __shared__ SHA1_CTX workspace[THREADS_PER_BLOCK];

    SHA1_CTX &ctx = workspace[threadIdx.x];

    Nonce &target = target[blockIdx.x];

    uint64_t initial_hash_value = 0;
    uint64_t hash_value = initial_hash_value;

    Nonce nonce;
    do {
        hash_value++;
        *((uint64_t*)&nonce) = hash_value;
        *((uint64_t*)&nonce + 1) = THREADS_PER_BLOCK * blockIdx.x + threadIdx.x;
        ctx = original;
        if(mine_single_fast(ctx, nonce, );

    } while ((hash_value < initial_hash_value + limit));

}

Nonce mine() {

}

void test_cuda() {
    int host_[N], hb[N];

    int *da, *db;
    if(cudaMalloc((void **)&da, N*sizeof(int))){
        std::cout << "Failed to" << std::endl;
    }

    cudaMalloc((void **)&db, N*sizeof(int));

    //
    // Initialise the input data on the CPU.
    //
    for (int i = 0; i<N; ++i) {
        ha[i] = i;
    }

    //
    // Copy input data to array on GPU.
    //
    cudaMemcpy(da, ha, N*sizeof(int), cudaMemcpyHostToDevice);

    //
    // Launch GPU code with N threads, one per
    // array element.
    //
    add<<<N, 1>>>(da, db);

    //
    // Copy output array from GPU back to CPU.
    //
    cudaMemcpy(hb, db, N*sizeof(int), cudaMemcpyDeviceToHost);

    for (int i = 0; i<N; ++i) {
        printf("%d\n", hb[i]);
    }

    //
    // Free up the arrays on the GPU.
    //
    cudaFree(da);
    cudaFree(db);
}

