#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 11 16:24:10 2019

@author: Enver
"""

import random 
from math import gcd 

def prime(n):
    count = 0 
    for i in range(1,n):
        if n % i == 0:
            count +=1
    if count == 1:
        return True 
    else:
        return False

def get_primes():
    p = 0
    q = 0 
    while not (prime(p) and prime(q) and p != q):
        p = random.randint(2,100)
        q = random.randint(2,100)
    return p, q

def get_n(p, q):
    n = p * q 
    return n

def get_phi(p, q):
    phi = ((p - 1)) * ((q - 1))
    return phi

def get_primefactors(n):
    factors = []
    for i in range(1, n+1):
        if n % i == 0:
            factors.append(i)
    return factors

def get_coprimes(n, factors):
    coprimes = []
    for i in factors:
        if gcd(n, i) == 1:
            coprimes.append(i)
    return coprimes

def get_e(n , phi):
    phi_factors = get_primefactors(phi)
    n_factors = get_primefactors(n)
    n_factors.extend(phi_factors)
    factors = set(n_factors)
    x = []
    for i in range (2, (phi + 1)):
        lst = get_coprimes(i, factors)
        x.extend(lst)
    e = random.choice(x)
    return e

def get_d(e, phi):
    lst = []
    for n in range(3, phi):
        if ((e * n) % phi) == 1:
            lst.append(n)
    if lst == []:
        return None
    d = random.choice(lst)
    return d

def generate_keys():
    d = None 
    while d == None:
        p, q = get_primes()
        n = get_n(p, q)
        phi = get_phi(p, q)
        e = get_e(n, phi)
        d = get_d(e, phi)
    return (e,n), (d,n)

def encrypt (msg, key):
    encrypted = ''
    for i in msg: 
        s = (ord(i)**key[0]) % key[1]
        encrypted += chr(s)
    return encrypted 











