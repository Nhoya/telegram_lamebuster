#!/usr/bin/python3

limite = 3
media = 6
a = 0.4
times = [19,20,21,22,23,24,25]
time_old = times[0]

for t in times[1:]:
    time = t
    differenza = time - time_old
    print("Vecchio time: "+str(time_old))
    time_old = time
    media = a*media+(1-a)*(differenza)

    print("Nuovo time: "+str(time))
    print("Differenza: "+str(differenza))
    print("Media: "+str(media))
    print("Limite: "+str(limite))
    print("a: "+str(a)+"\n")

    if media <= limite:
        print("Utente Bannato")
        exit(0)
