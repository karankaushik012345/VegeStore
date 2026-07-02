import React, { createContext, useContext, useState, useEffect } from 'react';
import { cartAPI } from '../api';
import { useAuth } from './AuthContext';
import toast from 'react-hot-toast';

const CartContext = createContext(null);

export function CartProvider({ children }) {
  const [items, setItems] = useState([]);
  const { user } = useAuth();

  useEffect(() => {
    if (user) cartAPI.get().then(r => setItems(r.data)).catch(() => {});
    else setItems([]);
  }, [user]);

  const addToCart = async (productId, qty=1) => {
    if (!user) { toast.error('Please login to add to cart'); return; }
    try {
      await cartAPI.add(productId, qty);
      const r = await cartAPI.get();
      setItems(r.data);
      toast.success('Added to cart! 🛒');
    } catch(e) { toast.error('Failed to add to cart'); }
  };

  const updateQty = async (itemId, qty) => {
    await cartAPI.update(itemId, qty);
    setItems(prev => qty <= 0 ? prev.filter(i => i.id !== itemId) : prev.map(i => i.id === itemId ? {...i, quantity: qty} : i));
  };

  const removeItem = async (itemId) => {
    await cartAPI.remove(itemId);
    setItems(prev => prev.filter(i => i.id !== itemId));
    toast.success('Removed from cart');
  };

  const clearCart = async () => {
    await cartAPI.clear();
    setItems([]);
  };

  const total = items.reduce((s, i) => s + i.product.price * i.quantity, 0);
  const count = items.reduce((s, i) => s + i.quantity, 0);

  return <CartContext.Provider value={{ items, total, count, addToCart, updateQty, removeItem, clearCart }}>{children}</CartContext.Provider>;
}

export const useCart = () => useContext(CartContext);