import React, { createContext, useContext, useState, useEffect } from 'react'  
import api from '../api/client.jsx'  
  
const UserContext = createContext(null)  
  
export const UserProvider = ({ children }) => {  
  const [user, setUser] = useState(null)  
  const [loading, setLoading] = useState(true)  
  
  const fetchUser = async () => {  
    try {  
      const token = localStorage.getItem('token')  
      if (!token) {  
        setLoading(false)  
        return  
      }  
        
      const res = await api.get('/users/me')  
      setUser(res.data)  
    } catch (err) {  
      console.error('Erreur chargement utilisateur:', err)  
      // Si le token est invalide, on nettoie  
      if (err.response?.status === 401) {  
        localStorage.removeItem('token')  
        localStorage.removeItem('refresh_token')  
        setUser(null)  
      }  
    } finally {  
      setLoading(false)  
    }  
  }  
  
  useEffect(() => {  
    fetchUser()  
  }, [])  
  
  const logout = () => {  
    localStorage.removeItem('token')  
    localStorage.removeItem('refresh_token')  
    setUser(null)  
  }  
  
  return (  
    <UserContext.Provider value={{ user, loading, fetchUser, logout }}>  
      {children}  
    </UserContext.Provider>  
  )  
}  
  
export const useUser = () => {  
  const context = useContext(UserContext)  
  if (!context) {  
    throw new Error('useUser doit être utilisé dans un UserProvider')  
  }  
  return context  
}