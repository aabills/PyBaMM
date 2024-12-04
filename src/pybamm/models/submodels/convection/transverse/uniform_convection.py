#
# Submodel for uniform convection in transverse directions
#
import pybamm
from .base_transverse_convection import BaseTransverseModel


class Uniform(BaseTransverseModel):
    """
    Submodel for uniform convection in transverse directions

    Parameters
    ----------
    param : parameter class
        The parameters to use for this submodel
    """

    def __init__(self, param):
        super().__init__(param)

    def build(self, submodels):
        p_s = pybamm.PrimaryBroadcast(0, "current collector")
        variables = self._get_standard_separator_pressure_variables(p_s)
        # Set up
        z = pybamm.standard_spatial_vars.z

        # Difference in negative and positive electrode velocities determines the
        # velocity in the separator
        i_boundary_cc = pybamm.CoupledVariable(
            "Current collector current density [A.m-2]",
            domain="current collector",
        )
        self.coupled_variables.update({i_boundary_cc.name: i_boundary_cc})
        v_box_n_right = -self.param.n.DeltaV * i_boundary_cc / self.param.F
        v_box_p_left = -self.param.p.DeltaV * i_boundary_cc / self.param.F
        d_vbox_s_dx = (v_box_p_left - v_box_n_right) / self.param.s.L

        # Simple formula for velocity in the separator
        div_Vbox_s = -d_vbox_s_dx
        variables.update(
            self._get_standard_transverse_velocity_variables(div_Vbox_s, "acceleration")
        )

        Vbox_s = pybamm.IndefiniteIntegral(div_Vbox_s, z)
        variables.update(
            self._get_standard_transverse_velocity_variables(Vbox_s, "velocity")
        )

        self.variables.update(variables)
