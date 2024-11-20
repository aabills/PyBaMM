#
# Full model of electrode employing Ohm's law
#
import pybamm
from .base_ohm import BaseModel
from pybamm.doc_utils import copy_parameter_doc_from_parent, doc_extend_parent


@copy_parameter_doc_from_parent
@doc_extend_parent
class Full(BaseModel):
    """Full model of electrode employing Ohm's law."""

    def __init__(self, param, domain, options=None):
        super().__init__(param, domain, options=options)

    def build(self):
        domain, Domain = self.domain_Domain

        if domain == "negative":
            reference = 0
        else:
            reference = self.param.ocv_init

        phi_s = pybamm.Variable(
            f"{Domain} electrode potential [V]",
            domain=f"{domain} electrode",
            auxiliary_domains={"secondary": "current collector"},
            reference=reference,
        )
        phi_s.print_name = f"phi_s_{domain[0]}"

        phi_s_cn = pybamm.CoupledVariable(
            "Negative current collector potential [V]", domain="current collector"
        )
        self.coupled_variables.update(
            {"Negative current collector potential [V]": phi_s_cn}
        )

        tor = pybamm.CoupledVariable(
            f"{Domain} electrode transport efficiency", domain=f"{domain} electrode"
        )
        self.coupled_variables.update({f"{Domain} electrode transport efficiency": tor})

        T = pybamm.CoupledVariable(
            f"{Domain} electrode temperature [K]", domain=f"{domain} electrode"
        )
        self.coupled_variables.update({f"{Domain} electrode temperature [K]": T})

        sum_a_j = pybamm.CoupledVariable(
            f"Sum of {domain} electrode volumetric interfacial current densities [A.m-3]",
            domain=f"{domain} electrode",
        )
        self.coupled_variables.update(
            {
                f"Sum of {domain} electrode volumetric interfacial current densities [A.m-3]": sum_a_j
            }
        )

        variables = self._get_standard_potential_variables(phi_s)
        self.variables.update(variables)

        sigma = self.domain_param.sigma(T)
        sigma_eff = sigma * tor
        i_s = -sigma_eff * pybamm.grad(phi_s)
        self.variables.update({f"{Domain} electrode effective conductivity": sigma_eff})
        self.variables.update(self._get_standard_current_variables(i_s))

        if self.domain == "positive":
            self.variables.update(
                self._get_standard_whole_cell_variables(
                    {**self.variables, **self.coupled_variables}
                )
            )

        self.algebraic[phi_s] = self.param.L_x**2 * (pybamm.div(i_s) + sum_a_j)

        if self.domain == "negative":
            lbc = (phi_s_cn, "Dirichlet")
            rbc = (pybamm.Scalar(0), "Neumann")

        elif self.domain == "positive":
            lbc = (pybamm.Scalar(0), "Neumann")
            sigma_eff = self.param.p.sigma(T) * tor
            i_boundary_cc = pybamm.CoupledVariable(
                "Current collector current density [A.m-2]", domain="current collector"
            )
            rbc = (
                i_boundary_cc / pybamm.boundary_value(-sigma_eff, "right"),
                "Neumann",
            )

        self.boundary_conditions[phi_s] = {"left": lbc, "right": rbc}

        if self.domain == "negative":
            phi_s_init = pybamm.Scalar(0)
        else:
            phi_s_init = self.param.ocv_init

        self.initial_conditions[phi_s] = phi_s_init
