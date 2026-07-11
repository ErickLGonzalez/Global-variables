"""B9 quantum layer: the 1985 protocol in miniature.

Historical protocol (R18): junction parameters were measured in the
CLASSICAL regime, the Schroedinger problem was solved numerically, and
the predicted quantum resonances were compared to data WITHOUT refitting
-- our promotion criterion 5 (novel prediction on a held-out DOMAIN),
executed in 1985.

Here: 'classical calibration' supplies rational (E_C, E_J); the
charge-basis Hamiltonian is built EXACTLY (Fractions):

    H_{nn'} = 4 E_C (n - n_g)^2 delta_{nn'} - (E_J/2)(delta_{n,n'+1} +
              delta_{n,n'-1})

and its spectrum (numerical layer, truncation-audited) must reproduce
the independent transmon asymptotics E_01 ~ sqrt(8 E_J E_C) - E_C and
anharmonicity ~ -E_C -- predictions the calibration never saw.
Escape widths are OUT OF SCOPE for a hard-wall truncation (recorded
stipulation: level positions yes, tunneling rates no)."""

from fractions import Fraction
import numpy as np


def charge_basis_H(EC: Fraction, EJ: Fraction, ng: Fraction, ncut: int):
    """Exact rational tridiagonal Hamiltonian, n = -ncut..ncut."""
    EC, EJ, ng = Fraction(EC), Fraction(EJ), Fraction(ng)
    N = 2 * ncut + 1
    H = [[Fraction(0)] * N for _ in range(N)]
    for i, n in enumerate(range(-ncut, ncut + 1)):
        H[i][i] = 4 * EC * (Fraction(n) - ng) ** 2
        if i + 1 < N:
            H[i][i + 1] = -EJ / 2
            H[i + 1][i] = -EJ / 2
    return H


def spectrum(H, k=4):
    Hf = np.array([[float(x) for x in row] for row in H])
    ev = np.linalg.eigvalsh(Hf)
    return ev[:k]


def heldout_spectroscopy(EC=Fraction(1, 4), EJ=Fraction(25, 2),
                         ng=Fraction(1, 2)):
    """Returns predicted transitions plus the independent asymptotic
    check and the truncation-convergence audit."""
    e_small = spectrum(charge_basis_H(EC, EJ, ng, ncut=10))
    e_big = spectrum(charge_basis_H(EC, EJ, ng, ncut=20))
    trunc = float(np.max(np.abs(e_small - e_big)))
    E01 = float(e_big[1] - e_big[0])
    E12 = float(e_big[2] - e_big[1])
    ECf, EJf = float(EC), float(EJ)
    E01_asym = np.sqrt(8 * EJf * ECf) - ECf
    anharm = E12 - E01
    return {"E01": E01, "E12": E12,
            "E01_asymptotic_prediction": E01_asym,
            "E01_rel_dev_from_asymptotic": abs(E01 - E01_asym) / E01_asym,
            "anharmonicity": anharm, "anharmonicity_prediction": -ECf,
            "truncation_convergence": trunc,
            "stipulations": ["hard-wall truncation: level POSITIONS only; "
                             "escape widths require outgoing-wave/CAP "
                             "boundary conditions (out of scope)",
                             "EJ/EC = 50: transmon asymptotic regime"]}
