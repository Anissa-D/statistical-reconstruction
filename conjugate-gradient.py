import matplotlib.pyplot as plt
import numpy as np
from scipy import optimize

A = np.genfromtxt('gene_1182_nettoye.txt', missing_values = 'NA', filling_values = np.nan, skip_header = 1)
AA = A[:, 3].reshape(2, 4, 11)
C, R, N = AA.shape
# vecteur des temps
T = np.array([0, 0.5, 1, 3.5, 6.5, 9.25, 12.5, 18.5, 22.5, 26.5, 30.5])
# vecteur des eta, niveaux d'activité du facteur de transcription
B = np.genfromtxt('TF_2617_M.txt', missing_values = 'NA', filling_values = np.nan, skip_header = 1)
etaAM = B[:, 2].reshape(2, 11)

def theorie(temps, c):
    N = temps.size
    eta = etaAM[c, :]
    resultat = np.zeros(N)
    for n in range(N): # entrée dans la boucle sur les temps
        t = temps[n]
        ### calcul d'une somme utile dans mu_{c}(t) qui dépend de t, donc de n
        somme = 0
#        coef = np.zeros(n)
        for j in range(n):
#            coef[j] = ( eta[j+1] / (gamma + eta[j+1]) + eta[j] / (gamma + eta[j]) ) / 2
            somme += (np.exp(delta*temps[j+1])-np.exp(delta*temps[j])) * eta[j] / (gamma + eta[j])
        ### fin de ce calcul
        # calcul de mu_c(t)
        resultat[n] = (mu0 - alpha/delta) * np.exp(-delta*t) + alpha/delta + beta*np.exp(-delta*t)/delta*somme
    return resultat

def mesure(temps):
    # on prend g_{0, r}(t) dans le vecteur AA et on fait la moyenne sur les réplicats
    resultatA = AA[0, :, :].mean(axis = 0)
    # on prend g_{1, r}(t) dans le vecteur AA et on fait la moyenne sur les réplicats
    resultatM = AA[1, :, :].mean(axis = 0)
    return resultatA, resultatM

def ml(x): # moins l
    ml = 0
    alphaA, betaA, gammaA, deltaA, mu0A, alphaM, betaM, gammaM, deltaM, mu0M, sigma = x
    for c in range(C): # entrée dans la boucle sur les conditions
        eta = etaAM[c, :]
        if c == 0: # faisons d'abord la condition alginate
            alpha, beta, gamma, delta, mu0 = alphaA, betaA, gammaA, deltaA, mu0A
        if c == 1:
            alpha, beta, gamma, delta, mu0 = alphaM, betaM, gammaM, deltaM, mu0M
        for n in range(N): # entrée dans la boucle sur les temps
            t = T[n]
            ### calcul d'une somme utile dans mu_{c}(t) qui dépend de t, donc de n
            somme = 0
            for j in range(n): # à faire : améliorer rectangle -> trapèze
                somme += (np.exp(delta*T[j+1])-np.exp(delta*T[j])) * eta[j] / (gamma + eta[j])
            ### fin de ce calcul
            # calcul de mu_c(t)
            muct = (mu0 - alpha/delta) * np.exp(-delta*t) + alpha/delta + beta*np.exp(-delta*t)/delta*somme
            for r in range(R):
                # on prend g_{c, r}(t) dans le vecteur AA
                gcrt = AA[c, r, n]
                # à ce moment, on dispose de gcrt, et aussi de muct, on peut calculer la somme
                ml += (np.log(gcrt/muct) / sigma + sigma / 2)**2 / 2 + np.log(np.sqrt(2*np.pi)*gcrt) + np.log(sigma)
    return ml

"""
def gradml(x):
    alphaA, betaA, gammaA, deltaA, mu0A, alphaM, betaM, gammaM, deltaM, mu0M, sigma = x

    return np.asarray((dalphaA, dbetaA, dgammaA, ddeltaA, dmu0A, dalphaM, dbetaM, dgammaM, ddeltaM, dmu0M, dsigma))
"""

mu0 = AA[0, 0, 0]
x0 = np.asarray((1, 1, 1, 1, mu0, 1, 1, 1, 1, mu0, 1)) # Initial guess
bnds = ((0, None), (0, None), (0, None), (0, None), (0, None), (0, None), (0, None), (0, None), (0, None), (0, None), (0, None))
# res1 = optimize.fmin_cg(ml, x0, fprime = gradml, args = eta)
# res1 = optimize.fmin_cg(ml, x0)
res1 = optimize.minimize(ml, x0, bounds=bnds)

## résultats de l'optimisation
alphaA, betaA, gammaA, deltaA, mu0A, alphaM, betaM, gammaM, deltaM, mu0M, sigma = res1.x
alpha, beta, gamma, delta, mu0 = alphaA, betaA, gammaA, deltaA, mu0A
resultatA = theorie(T, 0)
alpha, beta, gamma, delta, mu0 = alphaM, betaM, gammaM, deltaM, mu0M
resultatM = theorie(T, 1)

## mesures
observationA, observationM = mesure(T)

# 1. Create a figure of size 8x6 inches, 80 dots per inch
figure1 = plt.figure(figsize=(8, 6), dpi=80)
figure1.canvas.set_window_title('My title')
# 1.5 Optional create a new subplot from a grid of 1x2
plt.subplot(1,2,1)
# 2. Plot (T, resultatA)
plt.plot(T, resultatA, '-', label='mu alginate')
plt.plot(T, observationA, 'o', label='g alginate')
plt.legend()
plt.grid(True)
plt.subplot(1,2,2)
# 2. Plot (T, resultatM)
plt.plot(T, resultatM, '-', label='mu maltose')
plt.plot(T, observationM, 'o', label='g maltose')
plt.legend()
plt.grid(True)
# 3. Show result on screen
plt.show()
