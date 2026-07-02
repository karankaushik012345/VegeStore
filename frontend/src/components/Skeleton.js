
import React from 'react';
import './Skeleton.css';

export function SkeletonCard() {
  return (
    <div className="skeleton-card">
      <div className="skeleton-img skeleton-pulse"></div>
      <div className="skeleton-body">
        <div className="skeleton-line short skeleton-pulse"></div>
        <div className="skeleton-line skeleton-pulse"></div>
        <div className="skeleton-line medium skeleton-pulse"></div>
        <div className="skeleton-footer">
          <div className="skeleton-price skeleton-pulse"></div>
          <div className="skeleton-btn skeleton-pulse"></div>
        </div>
      </div>
    </div>
  );
}

export function SkeletonGrid({ count = 10 }) {
  return (
    <div className="skeleton-grid">
      {Array.from({ length: count }).map((_, i) => <SkeletonCard key={i} />)}
    </div>
  );
}

export function SkeletonDetail() {
  return (
    <div className="skeleton-detail">
      <div className="skeleton-detail-img skeleton-pulse"></div>
      <div className="skeleton-detail-info">
        <div className="skeleton-line short skeleton-pulse"></div>
        <div className="skeleton-line skeleton-pulse" style={{height:28,marginBottom:12}}></div>
        <div className="skeleton-line medium skeleton-pulse"></div>
        <div className="skeleton-line skeleton-pulse" style={{height:40,marginTop:16}}></div>
        <div className="skeleton-line short skeleton-pulse" style={{height:48,marginTop:16}}></div>
        <div className="skeleton-line skeleton-pulse" style={{height:52,marginTop:16,borderRadius:8}}></div>
      </div>
    </div>
  );
}

export function SkeletonBanner() {
  return <div className="skeleton-banner skeleton-pulse"></div>;
}
