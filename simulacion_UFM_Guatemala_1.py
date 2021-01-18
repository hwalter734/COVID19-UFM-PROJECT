import matplotlib.pyplot as plt
import matplotlib.animation as ani
import numpy as np
from numpy.lib.arraypad import pad

#Los valores son con el formato de RGB
GRIS = (0.78, 0.78, 0.78)  # no infectados
ROJO = (0.96, 0.15, 0.15)   # infectados
VERDE = (0, 0.86, 0.03)    # recuperados
NEGRO = (0, 0, 0)          # muertos

# El primer valor de recuperados(servero y crítico) representa el menor número de días que toma recuperarse
#El segundo valor de recuperados(servero y crítico) representa el mayor número de días que toma recuperarse

COVID19_PARAMS = {

    "r0": 0.59,
    "incubation": 5,
    "p_moderado": 0.95,
    "moderado_recuperado": (7, 14), 
    "p_critico": 0.05,
    "critico_recuperado": (21, 42),
    "critico_muerte": (14, 56),
    "tasa_mortalidad": 0.034,
    "intervalo_serie": 3

}


class Virus():
    def __init__(self, params):
        self.fig = plt.figure()
        self.axes = self.fig.add_subplot(111, projection = "polar")
        self.axes.grid(False)
        self.axes.set_xticklabels([])
        self.axes.set_yticklabels([])
        self.axes.set_ylim(0, 1)
        self.axes.set_title('COVID-19 UFM Guatemala 1 Infectado Inicial', loc = 'center', y = 1, pad = 14)
        self.dia_text = self.axes.annotate("Día 0", xy = [np.pi / 2, 1], ha = "center", va = "bottom")
        self.infectado_text = self.axes.annotate("Infectados: 0", xy = [3 * np.pi / 2, 1], ha = "center", va = "top", color = ROJO)
        self.muertes_text = self.axes.annotate("\nMuertes: 0", xy = [3 * np.pi / 2, 1], ha = "center", va = "top", color = NEGRO)
        self.recuperado_text = self.axes.annotate("\n\nRecuperados: 0", xy = [3 * np.pi / 2, 1], ha = "center", va = "top", color = VERDE)

        self.dia = 0
        self.total_num_infectado = 0
        self.num_currently_infectado = 0
        self.num_recuperado = 0
        self.num_muertes = 0
        self.r0 = params["r0"]
        self.p_moderado = params["p_moderado"]
        self.p_critico = params["p_critico"]
        self.tasa_mortalidad = params["tasa_mortalidad"]
        self.intervalo_serie = params["intervalo_serie"]

        self.moderado_rapido = params["incubation"] + params["moderado_recuperado"][0]
        self.moderado_lento = params["incubation"] + params["moderado_recuperado"][1]
        self.critico_rapido = params["incubation"] + params["critico_recuperado"][0]
        self.critico_lento = params["incubation"] + params["critico_recuperado"][1]
        self.muerte_rapido = params["incubation"] + params["critico_muerte"][0]
        self.muerte_lento = params["incubation"] + params["critico_muerte"][1]

        self.moderado = {i: {"thetas": [], "rs": []} for i in range(self.moderado_rapido, 365)}
        self.critico = {
            'recuperado': {i: {"thetas": [], "rs": []} for i in range(self.critico_rapido, 365)},
            'muerte': {i: {"thetas": [], "rs": []} for i in range(self.muerte_rapido, 365)}
        }

        self.expuesto_antes = 0
        self.expuesto_despues = 1

        self.poblacion_inicial()


    def poblacion_inicial(self):
        poblacion = 4000
        self.num_currently_infectado = 1
        self.total_num_infectado = 1
        indices = np.arange(0, poblacion) + 0.5
        self.thetas = np.pi * (1 + pow(5, 0.5)) * indices
        self.rs = np.sqrt(indices / poblacion)
        self.plot = self.axes.scatter(self.thetas, self.rs, s = 5, color = GRIS)
        self.axes.scatter(self.thetas[0], self.rs[0], s = 5, color = ROJO)
        self.moderado[self.moderado_rapido]["thetas"].append(self.thetas[0])
        self.moderado[self.moderado_rapido]["rs"].append(self.rs[0])


    def esparcir_virus(self, i):
        self.expuesto_antes = self.expuesto_despues
        if self.dia % self.intervalo_serie == 0 and self.expuesto_antes < 4000:
            self.num_new_infectado = round(self.r0 * self.total_num_infectado)
            self.expuesto_despues += round(self.num_new_infectado * 1.1)
            if self.expuesto_despues > 4000:
                self.num_new_infectado = round((4000 - self.expuesto_antes) * 0.9)
                self.expuesto_despues = 4000
            self.num_currently_infectado += self.num_new_infectado
            self.total_num_infectado += self.num_new_infectado
            self.new_infectado_indices = list(
                np.random.choice(
                    range(self.expuesto_antes, self.expuesto_despues),
                    self.num_new_infectado,
                    replace = False))
            thetas = [self.thetas[i] for i in self.new_infectado_indices]
            rs = [self.rs[i] for i in self.new_infectado_indices]
            self.anim.event_source.stop()
            if len(self.new_infectado_indices) > 12:
                size_list = round(len(self.new_infectado_indices) / 12)
                theta_chunks = list(self.chunks(thetas, size_list))
                r_chunks = list(self.chunks(rs, size_list))
                self.anim2 = ani.FuncAnimation(
                    self.fig,
                    self.uno_por_uno,
                    interval = 100,
                    frames = len(theta_chunks),
                    fargs = (theta_chunks, r_chunks, ROJO))
            else:
                self.anim2 = ani.FuncAnimation(
                    self.fig,
                    self.uno_por_uno,
                    interval = 100,
                    frames = len(thetas),
                    fargs = (thetas, rs, ROJO))
            self.asignar_sintomas()

        self.dia += 1

        self.actualizar_estado()
        self.actualizar_texto()


    def uno_por_uno(self, i, thetas, rs, color):
        self.axes.scatter(thetas[i], rs[i], s = 5, color = color)
        if i == (len(thetas) - 1):
            self.anim2.event_source.stop()
            self.anim.event_source.start()


    def chunks(self, a_list, n):
        for i in range(0, len(a_list), n):
            yield a_list[i:i + n]


    def asignar_sintomas(self):
        num_moderado = round(self.p_moderado * self.num_new_infectado)
        num_critico = round(self.p_critico * self.num_new_infectado)
        self.indices_moderados = np.random.choice(self.new_infectado_indices, num_moderado, replace = False)
        indices_restantes = [i for i in self.new_infectado_indices if i not in self.indices_moderados]
        p_critico_recuperado = 1 - (self.tasa_mortalidad / self.p_critico)
        num_critico_recuperado = round(p_critico_recuperado * num_critico)
        self.indices_criticos = []
        self.indices_muertes = []
        if indices_restantes:
            self.indices_criticos = np.random.choice(indices_restantes, num_critico_recuperado, replace = False)
            self.indices_muertes = [i for i in indices_restantes if i not in self.indices_criticos]

        low = self.dia + self.moderado_rapido
        high = self.dia + self.moderado_lento
        for mild in self.indices_moderados:
            dia_recuperado = np.random.randint(low, high)
            mild_theta = self.thetas[mild]
            mild_r = self.rs[mild]
            self.moderado[dia_recuperado]["thetas"].append(mild_theta)
            self.moderado[dia_recuperado]["rs"].append(mild_r)

        low = self.dia + self.critico_rapido
        high = self.dia + self.critico_lento
        for recuperado in self.indices_criticos:
            dia_recuperado = np.random.randint(low, high)
            recuperado_theta = self.thetas[recuperado]
            recuperado_r = self.rs[recuperado]
            self.critico["recuperado"][dia_recuperado]["thetas"].append(recuperado_theta)
            self.critico["recuperado"][dia_recuperado]["rs"].append(recuperado_r)

        low = self.dia + self.muerte_rapido
        high = self.dia + self.muerte_lento
        for muerte in self.indices_muertes:
            muerte_dia = np.random.randint(low, high)
            muerte_theta = self.thetas[muerte]
            muerte_r = self.rs[muerte]
            self.critico["muerte"][muerte_dia]["thetas"].append(muerte_theta)
            self.critico["muerte"][muerte_dia]["rs"].append(muerte_r)


    def actualizar_estado(self):
        if self.dia >= self.moderado_rapido:
            moderado_thetas = self.moderado[self.dia]["thetas"]
            moderado_rs = self.moderado[self.dia]["rs"]
            self.axes.scatter(moderado_thetas, moderado_rs, s = 5, color = VERDE)
            self.num_recuperado += len(moderado_thetas)
            self.num_currently_infectado -= len(moderado_thetas)
        if self.dia >= self.critico_rapido:
            rec_thetas = self.critico["recuperado"][self.dia]["thetas"]
            rec_rs = self.critico["recuperado"][self.dia]["rs"]
            self.axes.scatter(rec_thetas, rec_rs, s = 5, color = VERDE)
            self.num_recuperado += len(rec_thetas)
            self.num_currently_infectado -= len(rec_thetas)
        if self.dia >= self.muerte_rapido:
            muerte_thetas = self.critico["muerte"][self.dia]["thetas"]
            muerte_rs = self.critico["muerte"][self.dia]["rs"]
            self.axes.scatter(muerte_thetas, muerte_rs, s = 5, color = NEGRO)
            self.num_muertes += len(muerte_thetas)
            self.num_currently_infectado -= len(muerte_thetas)


    def actualizar_texto(self):
        self.dia_text.set_text("Día {}".format(self.dia))
        self.infectado_text.set_text("Infectados: {}".format(self.num_currently_infectado))
        self.muertes_text.set_text("\nMuertes: {}".format(self.num_muertes))
        self.recuperado_text.set_text("\n\nRecuperados: {}".format(self.num_recuperado))


    def gen(self):
        while self.num_muertes + self.num_recuperado < self.total_num_infectado:
            yield


    def animate(self):
        self.anim = ani.FuncAnimation(
            self.fig,
            self.esparcir_virus,
            frames = self.gen,
            repeat = True)


def main():
    coronavirus = Virus(COVID19_PARAMS)
    coronavirus.animate()
    plt.show()


if __name__ == "__main__":
    main()