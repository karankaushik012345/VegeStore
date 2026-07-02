
import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { productsAPI, wishlistAPI } from '../api';
import ProductCard from '../components/ProductCard';
import { SkeletonGrid } from '../components/Skeleton';
import { Filter, SlidersHorizontal, ChevronRight } from 'lucide-react';
import './Products.css';

export default function Products() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [products, setProducts] = useState([]);
  const [total, setTotal] = useState(0);
  const [pages, setPages] = useState(1);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [categories, setCategories] = useState([]);
  const [wishlistIds, setWishlistIds] = useState([]);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    q: searchParams.get('q') || '',
    category: searchParams.get('category') || '',
    sort: 'featured',
    organic: searchParams.get('organic') === 'true',
  });

  const fetchWishlist = useCallback(() => {
    const token = localStorage.getItem('token');
    if (token) wishlistAPI.get().then(r => setWishlistIds(r.data.map(i => i.product.id))).catch(() => {});
  }, []);

  useEffect(() => {
    productsAPI.getCategories().then(r => setCategories(r.data));
    fetchWishlist();
  }, [fetchWishlist]);

  useEffect(() => {
    setLoading(true);
    const params = { ...filters, organic: filters.organic ? 'true' : '', page, per_page: 20 };
    productsAPI.getAll(params).then(r => {
      setProducts(r.data.products);
      setTotal(r.data.total);
      setPages(r.data.pages);
      setLoading(false);
    });
  }, [filters, page]);

  const setFilter = (key, val) => { setFilters(f => ({...f, [key]: val})); setPage(1); };

  const pageTitle = filters.q
    ? `Results for "${filters.q}"`
    : filters.category || 'All Vegetables';

  return (
    <div className="products-page">
      <div className="container">

        {/* Breadcrumb */}
        <div className="breadcrumb" style={{marginBottom:16}}>
          <Link to="/">Home</Link>
          <ChevronRight size={14} />
          <span>Shop</span>
          {filters.category && <><ChevronRight size={14} /><span>{filters.category}</span></>}
        </div>

        <div className="products-layout">
          <aside className={`filters-sidebar ${showFilters ? 'open' : ''}`}>
            <div className="filter-section">
              <h3><Filter size={15} /> Filters</h3>
            </div>
            <div className="filter-section">
              <label className="filter-label">Category</label>
              <div className="category-filter-list">
                <button className={`cat-filter-btn ${!filters.category ? 'active' : ''}`} onClick={() => setFilter('category', '')}>
                  All Vegetables <span>{total}</span>
                </button>
                {categories.map(c => (
                  <button key={c.id} className={`cat-filter-btn ${filters.category===c.name ? 'active' : ''}`} onClick={() => setFilter('category', c.name)}>
                    <span>{c.icon} {c.name}</span>
                    <span>{c.count}</span>
                  </button>
                ))}
              </div>
            </div>
            <div className="filter-section">
              <label className="filter-label">Sort By</label>
              <select value={filters.sort} onChange={e => setFilter('sort', e.target.value)} className="filter-select">
                <option value="featured">Featured</option>
                <option value="rating">Top Rated</option>
                <option value="price_asc">Price: Low to High</option>
                <option value="price_desc">Price: High to Low</option>
                <option value="newest">Newest First</option>
              </select>
            </div>
            <div className="filter-section">
              <label className="filter-checkbox">
                <input type="checkbox" checked={filters.organic} onChange={e => setFilter('organic', e.target.checked)} />
                <span>🌱 Organic Only</span>
              </label>
            </div>
          </aside>

          <div className="products-main">
            <div className="products-header">
              <div>
                <h1>{pageTitle}</h1>
                <span className="product-count">{total.toLocaleString()} products found</span>
              </div>
              <button className="filter-toggle-btn" onClick={() => setShowFilters(f => !f)}>
                <SlidersHorizontal size={16} /> Filters
              </button>
            </div>

            {loading ? (
              <SkeletonGrid count={10} />
            ) : products.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">🥬</div>
                <h3>No vegetables found</h3>
                <p>Try different search terms or filters</p>
                <button className="btn-primary" style={{marginTop:16}} onClick={() => { setFilters({q:'',category:'',sort:'featured',organic:false}); setPage(1); }}>
                  Clear Filters
                </button>
              </div>
            ) : (
              <>
                <div className="products-grid-main">
                  {products.map(p => <ProductCard key={p.id} product={p} wishlistIds={wishlistIds} onWishlistChange={fetchWishlist} />)}
                </div>
                {pages > 1 && (
                  <div className="pagination">
                    <button className="page-btn" disabled={page === 1} onClick={() => setPage(p => p - 1)}>Prev</button>
                    {Array.from({length: pages}, (_, i) => i + 1).map(p => (
                      <button key={p} className={`page-btn ${page === p ? 'active' : ''}`} onClick={() => setPage(p)}>{p}</button>
                    ))}
                    <button className="page-btn" disabled={page === pages} onClick={() => setPage(p => p + 1)}>Next</button>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
