from scipy.integrate import quad
from scipy.interpolate import interp1d
import numpy as np
from math import sqrt


def stepFuncFactory(x_0, mag=1):
  def stepFunc(x):
    return   (0.5*(np.sign(x - x_0) + 1.0))*mag

  return stepFunc

#Only works in Wing spar, may need to 
#dim array contains:
#[lenth, radius, inner radius, height, base, t, flange height, flange width, web height, web width]
#I think t is the thickness of the rectangular beam
#besides array of dim Aircraft class requires E (youngs modulus), mag (magnitude of load), and type


def beam(AC):

	#returning max stress and deflection....... others?

	self.distLoadlist = []
  self.pointLoadFuncList = []
  self.pointMommentFuncList = []
  # print(self.distLoadlist)

  #spar is hollow circle
  if AC.Wing.spar.type == 'C':
    def calcI(self):

    def I(x):
      return 0.78*(dim[1]^^4-dim[2]^^4)

    self.I = I

  #spar is hollow rectangle
  elif AC.Wing.spar.type == 'R':
    def calcI(self):

    def I(x):
      return (AC.Wing.spar.dim[4]*AC.Wing.spar.dim[3]^^3-(AC.Wing.spar.dim[4]-2*t)(AC.Wing.spar.dim[3]-2t)^^3)

    self.I = I

  #spar is I-beam
  elif AC.Wing.spar.type == 'I':

    #this needs to be adjusted for new input method
    #not sure what X is and don't really know how to adjust this
    self.web_b = interp1d(self.X, self.web_dim[:,0])
    self.web_h = interp1d(self.X, self.web_dim[:,1])
    self.flange_b = interp1d(self.X, self.flange_dim[:,0])
    self.flange_h = interp1d(self.X, self.flange_dim[:,1])

    def calcI(self):

    def I(x):
      return 1.0/12.0*(self.web_b(x)*self.web_h(x)**3 + 2*self.flange_b(x)*self.flange_h(x)**3)


    self.I = I


 def addElipticalDistLoad(AC):
    # print(self.distLoadlist)
    def ellipticDist(x):
      B = AC.Wing.spar.mag/(np.pi*AC.Wing.spar.dim[0])
      y = sqrt( (1 - (x/AC.Wing.spar.dim[0])**2)*B**2 )
      return y

   	AC.distLoadlist.append(ellipticDist)



  def addDistLoad(AC,W, X):
      # self.distLoadlist.append(np.poly1d(np.polyfit(X,W, 3)))
    AC.distLoadlist.append(interp1d(X, W, kind='quadratic'))
      # return np.poly1d(np.polyfit(X,W, 4))




  def addPointLoad(AC, x_loc):
    AC.pointLoadFuncList.append(stepFuncFactory(x_loc,mag=mag))
    AC.Ry += AC.Wing.spar.mag



  def addPointMomment(AC, mag, x_loc):
    AC.pointMommentFuncList.append(stepFuncFactory(x_loc,mag=mag))
    AC.Rm += AC.Wing.spar.mag



  def calcDistLoad(AC):
    def distLoad(x):
      return sum( [func(x) for func in AC.distLoadlist])

    AC.distLoad = distLoad




  def calcShearForce(AC):

    def pointLoadFunc(x):
      if self.pointLoadFuncList:
       return sum( [func(x) for func in self.pointLoadFuncList])
      else:
        return 0.0

    self.pointLoadFunc = pointLoadFunc

    self.Ry += quad(self.distLoad,0, self.length)[0] #+ self.__mag


    def shearForce(x):

      

      # return sum( self.pointLoadFunc(x), self.distLoad(x) )
      return  -(self.Ry - self.pointLoadFunc(x) - quad(self.distLoad,0, x)[0] )


    self.shearForce = shearForce

  
