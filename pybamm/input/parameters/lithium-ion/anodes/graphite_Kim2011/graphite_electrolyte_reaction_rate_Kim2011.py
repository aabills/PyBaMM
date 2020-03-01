from pybamm import exp


def graphite_electrolyte_reaction_rate_Kim2011(T, T_inf, E_r, R_g):
    """
    Reaction rate for Butler-Volmer reactions between graphite and LiPF6 in EC:DMC
    [1].

    References
    ----------
    .. [1] Kim, G. H., Smith, K., Lee, K. J., Santhanagopalan, S., & Pesaran, A.
    (2011). Multi-domain modeling of lithium-ion batteries encompassing
    multi-physics in varied length scales. Journal of The Electrochemical
    Society, 158(8), A955-A969.

    Parameters
    ----------
    T : :class:`pybamm.Symbol`
        Dimensional temperature [K]
    T_inf: :class:`pybamm.Symbol`
        Reference temperature [K]
    E_r: :class:`pybamm.Symbol`
        Reaction activation energy [J.mol-1]
    R_g: :class:`pybamm.Symbol`
        The ideal gas constant [J.mol-1.K-1]

    Returns
    -------
    :class:`pybamm.Symbol`
        Reaction rate [(A.m-2)(m3.mol-1)^1.5]
    """

    i0_ref = 36  # reference exchange current density at 100% SOC
    sto = 0.36  # stochiometry at 100% SOC
    c_s_n_max = 2.87 * 10 ** 4  # max electrode concentration
    c_s_n_ref = sto * c_s_n_max  # reference electrode concentration
    c_e_ref = 1.2 * 10 ** 3  # reference electrolyte concentration
    alpha = 0.5  # charge transfer coefficient

    m_ref = (
        2
        * i0_ref
        / (c_e_ref ** alpha * (c_s_n_max - c_s_n_ref) ** alpha * c_s_n_ref ** alpha)
    )

    arrhenius = exp(E_r / R_g * (1 / T_inf - 1 / T))

    return m_ref * arrhenius
