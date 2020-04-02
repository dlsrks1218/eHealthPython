# eHealthPython

## 스마트워치의 건강데이터를 안전하게 수집하여 저장하는 방법

### 사용된 알고리즘
- DDP(Distributed Differential Privacy)
- Homomorphic Encryption 

### Reference
- ~~[https://github.com/Lab41/PySEAL](https://github.com/Lab41/PySEAL "Homomorphic Encryption Library") is a fork of Microsoft Research's homomorphic encryption implementation, the Simple Encrypted Arithmetic Library (SEAL). This code wraps the SEAL build in a docker container and provides Python API's to the encryption librar~~y
- [https://coderzcolumn.com/tutorials/python/paillier-homomorphic-encryption-phe](https://coderzcolumn.com/tutorials/python/paillier-homomorphic-encryption-phe "Paillier Homomorphic Encryption Scheme") is a public key homomorphic encryption scheme. Python library paillier provides implemetation of paillier cryptosystem.


* docker run -d -p 48888:8888 -e GRANT_SUDO=yes --user=root -v /home/hp/jupyter/ljh/eHealthPython:/home/jovyan/work --name eHealth_jupyter dlsrks1218/minimalnb-ehealth

* docker exec -it 'container ID' /bin/bash
