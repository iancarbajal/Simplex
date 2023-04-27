
import numpy as np

class Lp:
    
    def __init__(self, minmax ,funcionObjetivo, reestricciones,vars,varsLibres):
        """
        NOTA: UTILIZAMOS EL MISMO PPL PARA TODOS LOS EJEMPLOS DE LOS PARAMETROS.

        Respresenta el problema de programacion lineal como un objeto de python.
        
        Parametros:
            minmax: booleano que representa min(False) o max(True).

            funcionObjetivo: Diccionario de python representando los coeficientes de la funcion objetivo, 
            donde las llaves son las variables y los valores los coeficientes.
            EJEMPLO: {"x": 3, "y": 4}

            reestricciones: Una lista de diccionarios de python representando las reestricciones.
            Tiene llaves "variables"(un diccionario de los nombres de las variables y sus coeficientes),
            "relacion"("<=",">=" o "=") y "val" (el valor constante del lado derecho de la reestriccion).
            EJEMPLO: [
                        {"variables": {"x": 1, "y": 2}, "relacion": "<=", "val": 5},
                        {"variables": {"x": 2, "y": 1}, "relacion": "<=", "val": 8},
                     ]

            vars: Una lista con el nombre de todas las variables del PPL.
            EJEMPLO: ["x","y"]

            varsLibres: Una lista con el nombre de todas las variables libres del PPL.
            La clase asume que todas las variables que no esten en esta lista son mayores o iguales a cero.
            EJEMPLO: [] (YA QUE NO HAY VARIABLES LIBRES)
        """
        self.minmax=minmax
        self.vars=vars
        self.varsLibres=varsLibres
        self.funcionObjetivo = funcionObjetivo
        self.reestricciones = reestricciones
        self.isEstandar=False
        
    def __str__(self):
        return f"Función Objetivo: {self.funcionObjetivo}\nReestricciones: {self.reestricciones}"
    
    def estandar(self):
        """
        Convierte el PPL en su forma estandar.

        Parametros:
            PPL ingresado por el usuario
        """
        # checamos si alguna de las variables es valor absoluto ||, max() o min() y agregamos las variables y reestricciones correspondientes
        c=1
        for var in list(self.funcionObjetivo):
            # Checa y pone las reestricciones con la funcion objetivo bien cuando hay una variable "|xi|" en la funcion objetivo
            if(var.startswith("|") and var.endswith("|")):
                self.vars.append("u"+str(c))
                index=self.vars.index(var[1:-1])
                for re in self.reestricciones:
                    re["variables"][self.vars[-1]]=0
                self.reestricciones.append({"variables":{varia: 0 for varia in self.vars},"relacion": "<=","val":0})
                self.reestricciones[-1]["variables"].update({self.vars[index]:1,self.vars[-1]:-1})
                self.reestricciones.append({"variables":{varia: 0 for varia in self.vars},"relacion": ">=","val":0})
                self.reestricciones[-1]["variables"].update({self.vars[index]:1,self.vars[-1]:1})

                val=self.funcionObjetivo.pop(var)
                self.funcionObjetivo[var[1:-1]]=0
                self.funcionObjetivo["u"+str(c)]=val
                c= c+ 1

            # Checa y pone las reestricciones con la funcion objetivo bien cuando hay "max(x1,x2,...)" en la funcion objetivo
            if(var.startswith("max(") and var.endswith(")")):
                varmax=var[4:-1].split(",")
                self.vars.append("u"+str(c))
                for re in self.reestricciones:
                    re["variables"][self.vars[-1]]=0
                for i in range(len(varmax)):
                    self.reestricciones.append({"variables":{varia: 0 for varia in self.vars},"relacion": ">=","val": 0})
                    self.reestricciones[-1]["variables"].update({varmax[i]:-1,self.vars[-1]:1})
                    if varmax[i] not in self.funcionObjetivo:
                        self.funcionObjetivo[varmax[i]]=0
                
                val=self.funcionObjetivo.pop(var)
                self.funcionObjetivo["u"+str(c)]=val
                c= c+1

            # Checa y pone las reestricciones con la funcion objetivo bien cuando hay "min(x1,x2,...)" en la funcion objetivo
            if(var.startswith("min(") and var.endswith(")")):
                varmin=var[4:-1].split(",")
                self.vars.append("u"+str(c))
                for re in self.reestricciones:
                    re["variables"][self.vars[-1]]=0
                for i in range(len(varmin)):
                    self.reestricciones.append({"variables":{varia: 0 for varia in self.vars},"relacion": "<=","val": 0})
                    self.reestricciones[-1]["variables"].update({varmin[i]:-1,self.vars[-1]:1})
                    if varmin[i] not in self.funcionObjetivo:
                        self.funcionObjetivo[varmin[i]]=0
                
                val=self.funcionObjetivo.pop(var)
                self.funcionObjetivo["u"+str(c)]=val
                c= c+1

            
        # Convertimos maximo en minimo.
        if(self.minmax):
            for variable in self.vars:
                self.funcionObjetivo[variable]= -self.funcionObjetivo[variable]
            self.minmax=False

        # Para todas las variables libres agregamos la variable necesaria a la funcion objetivo y a las reestricciones
        for varLibre in self.varsLibres:
            # Quito la variable libre y agrego la variable positiva y negativa a la funcion objetivo
            val=self.funcionObjetivo.pop(varLibre)
            self.funcionObjetivo[varLibre+"+"]=val
            self.funcionObjetivo[varLibre+"-"]=-val

            # Quito la variable libre y agrego la variable positiva y negativa a la lista de variables
            index=self.vars.index(varLibre)
            self.vars[index]=varLibre+"+"
            self.vars.insert(index+1, varLibre+"-")

            #Quito la variable libre y agrego la variable positiva y negativa a las reestricciones
            for reestriccion in self.reestricciones:
                val=reestriccion["variables"].pop(varLibre)
                reestriccion["variables"][varLibre+"+"]=val
                reestriccion["variables"][varLibre+"-"]=-val
        self.varsLibres=[]
        # Ya que tenemos todas las variables mayores o iguales a cero entonces agregamos las variables h1,h2,... para tener A@x=b.
        numH=len(self.reestricciones)
        Hs=["h"+str(i) for i in range(1,numH+1)]
        cont=1
        for rest in self.reestricciones:
            for i in range(numH):
                if(cont==(i+1)):
                    if(rest["relacion"]==">="):
                        rest["variables"][Hs[i]]=-1
                    else:
                        rest["variables"][Hs[i]]=1
                else:
                    rest["variables"][Hs[i]]=0
            rest["relacion"]="="
            cont=cont + 1
        self.isEstandar=True


    def toNumpy(self):
        """
        NOTA: Regresa las columnas en el orden que se encuentren en vars.

        Convierte el problema de programación lineal en su forma estandar y regresa los arreglos de numpy

        Parameters:
            problema de programacion lineal del objeto

        Returns:
            una tupla de arreglos de numpy (c, A, b) representando el problema en forma estandar:
            min c.T @ x
            sujeto A @ x = b
            x>=0
        """
        if(not self.isEstandar):
            self.estandar()

        Hs=["h"+str(i) for i in range(1,len(self.reestricciones)+1)]
        c = np.array([self.funcionObjetivo[var] for var in self.vars])
        A = np.array([[re["variables"][var] for var in self.vars+Hs] for re in self.reestricciones])
        b = np.array([re["val"] for re in self.reestricciones])
        return (c,A,b)
    
    def tabla0(self):
        c,A,b=self.toNumpy()
        cp=np.pad(c,(0,A.shape[1]-c.shape[0]+1), 'constant')
        bp=b[np.newaxis].T
        Ap=np.append(A,bp,axis=1)
        Ap=np.append(Ap,cp[np.newaxis],axis=0)

        return Ap

    #Esta función revisa que los costos relativos sean positivos
    #Si no lo son regresa un falso y si sí lo son regresa verdadero
    #De parámetros solicita n renglones y m columnas

    def __revisarCostosR(self,mat):
        return np.all(mat[-1,:-1]>=0)
    #revisa cuál de los valores cumple con el criterio del pivote

    def __variableEntrante(self,mat):
        return np.argwhere(mat[-1,:-1]<0)[0][0] # indice del costo negativo con valor absoluto más grande

    def __variableSaliente(self,mat,pos):
        # Obtén el renglon a pivotear y dar una excepcion si no esta acotado
        div = []
        divId = []
        for p in np.where(mat[:-1, pos] > 0)[0]:
            div.append(mat[p,-1] / mat[p,pos])
            divId.append(p)

        try:
            res = divId[div.index(min(div))]
        except ValueError:
            raise Exception('El problema es no acotado.')

        return res
    
    def __pivot(self,mat, ren, col):
        # cuantos renglones tiene la tabla
        reng= mat.shape[0]
        
        # dividimos entre pivote renglon
        pivot = mat[ren][col]
        mat[ren,:] = mat[ren,:] /pivot
        
        # operaciones elementales
        for i in range(reng):
            if i != ren:
                mat[i, :] = mat[i, :] + (-mat[i,col])*mat[ren, :]

        # Pasamos de -0 a 0
        m=reng-1
        for j in range(len(mat[m, :-1])):
            if mat[m, j] > -2e-15 and mat[m,j] < 0: 
                mat[m, j] = 0
        if mat[m, -1] > -2e-15 and mat[m,-1] < 0: 
            mat[m, -1] = 0
        
        return mat

    def simplex(self,mat):
        maxI=100000
        i=0
        while(not self.__revisarCostosR(mat) and i<maxI):
            e = self.__variableEntrante(mat)
            s = self.__variableSaliente(mat,e)
            mat= self.__pivot(mat, s, e)
            i=i+1
        if(i==maxI):
            print("NO HAY SOLUCIONES BASICAS FACTIBLES")
            return
        
        return mat
    
    def tabla0GranM(self): 
        c,A,b=self.toNumpy() 

        y=np.append(np.eye(len(self.reestricciones)),np.zeros(len(self.reestricciones))[np.newaxis],axis=0)
        A=np.append(self.tabla0()[:,:-1],y,axis=1)[:-1]
        cr=np.pad(self.tabla0()[-1,:-1],(0,len(self.reestricciones)),'constant',constant_values=100)

        Ap=np.append(A,cr[np.newaxis],axis=0)
        Ap =np.append(Ap,self.tabla0()[:,-1][np.newaxis].T,axis=1)
        Ap

        return Ap
    
    def tabla1GranM(self): 
        tabla0=self.tabla0GranM()
        
        col=self.tabla0().shape[1]-1
        ren=0
        for i in range(col,col+len(self.reestricciones)):
            tabla0=self.__pivot(tabla0,ren,i)
            ren=ren+1

        return tabla0
    
    def valida(self,mat):
        """
        Valida la matriz resultante del metodo de la gran M

        Regresa TRUE o FALSE
        """
        reng=mat.shape[0]
        col=self.tabla0().shape[1]-1
        for i in range(col,col+len(self.reestricciones)):
            for j in range(reng):
                if(i==j):
                    res=mat[j,i]==1
                else:
                    res=mat[j,i]==0
            if(res==True):
                break

        return res

    def sol(self,mat):
        #regresa una tupla con la solucion x y z_0
        x = np.zeros(mat.shape[1])
        colBas = np.where(mat[mat.shape[0]-1,:-1] == 0)[0]

        for j in colBas:
            indx = np.argmax(mat[:,j])
            x[j] = mat[indx,-1]

        return (x,-mat[-1,-1])


    def granM(self):
        res=self.simplex(self.tabla1GranM())
        try:
            if (self.valida(res)):
                raise ValueError
        except ValueError:
            raise Exception('El problema tiene region factible vacia')
        x,z0=self.sol(res)
        return (res,x,z0)