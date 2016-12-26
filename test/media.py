#!/usr/bin/python3
import math

max_messages = 5 # messages limit
max_lease = 2 # seconds between successive messages
pardon = 0.3
times = [19,20,21,22,23,26,27,28,29]
times = [19,20,23,26,29,32]
# inizia a 19 dopo tanto tempo
# spamma 4 messaggi (20,21,22,23)
# si stoppa per eludere il max_lease (26)
# spamma (26,27,28,29)

# l'algoritmo, dopo una sessione di spam inizia a perdonare l'utente
# per ogni messaggio non veloce che invia
# se l'utente torna a spammare viene bannato dopo pochi messaggi


#var
counter = 0
time_old = 0

for t in times:
    time = t
    lease = time - time_old
    print("Vecchio time: "+str(time_old))
    time_old = time
    if lease < max_lease:
        counter += 1
    else:
        if counter - pardon >= 0:
            counter -= pardon
        else:
            counter = 0

    print("Nuovo time: "+str(time))
    print("Differenza: "+str(lease))
    print("Counter: "+str(counter)+"\n")

    if math.ceil(counter) >= 5:
        print("Utente Bannato")
        exit(0)
