/**
 * Export Modal Component
 * Advanced data export system with multi-format support
 */

const { useState, useEffect, useCallback } = React;

function ExportModal() {
    // State management
    const [step, setStep] = useState(1);
    const [format, setFormat] = useState('csv');
    const [dateFrom, setDateFrom] = useState('');
    const [dateTo, setDateTo] = useState('');
    const [selectedCategories, setSelectedCategories] = useState([]);
    const [filename, setFilename] = useState('volunteer_opportunities');
    const [categories, setCategories] = useState([]);
    const [previewData, setPreviewData] = useState([]);
    const [totalCount, setTotalCount] = useState(0);
    const [totalVolunteers, setTotalVolunteers] = useState(0);
    const [loading, setLoading] = useState(false);
    const [previewLoading, setPreviewLoading] = useState(false);
    const [exporting, setExporting] = useState(false);
    const [exportSuccess, setExportSuccess] = useState(false);

    // Fetch categories on mount
    useEffect(() => {
        fetch('/api/categories/')
            .then(res => res.json())
            .then(data => setCategories(data.categories))
            .catch(err => console.error('Error fetching categories:', err));
    }, []);

    // Build query string for filters
    const buildQueryString = useCallback(() => {
        const params = new URLSearchParams();
        if (dateFrom) params.append('date_from', dateFrom);
        if (dateTo) params.append('date_to', dateTo);
        selectedCategories.forEach(cat => params.append('categories[]', cat));
        params.append('filename', filename);
        return params.toString();
    }, [dateFrom, dateTo, selectedCategories, filename]);

    // Fetch preview data
    const fetchPreview = useCallback(() => {
        setPreviewLoading(true);
        const params = new URLSearchParams();
        if (dateFrom) params.append('date_from', dateFrom);
        if (dateTo) params.append('date_to', dateTo);
        selectedCategories.forEach(cat => params.append('categories[]', cat));

        fetch(`/api/export/preview/?${params.toString()}`)
            .then(res => res.json())
            .then(data => {
                setPreviewData(data.opportunities);
                setTotalCount(data.total_count);
                setTotalVolunteers(data.total_volunteers);
                setPreviewLoading(false);
            })
            .catch(err => {
                console.error('Error fetching preview:', err);
                setPreviewLoading(false);
            });
    }, [dateFrom, dateTo, selectedCategories]);

    // Fetch preview when moving to step 2
    useEffect(() => {
        if (step === 2) {
            fetchPreview();
        }
    }, [step, fetchPreview]);

    // Handle category toggle
    const toggleCategory = (categoryId) => {
        setSelectedCategories(prev =>
            prev.includes(categoryId)
                ? prev.filter(id => id !== categoryId)
                : [...prev, categoryId]
        );
    };

    // Select all categories
    const selectAllCategories = () => {
        setSelectedCategories(categories.map(c => c.id.toString()));
    };

    // Clear all categories
    const clearAllCategories = () => {
        setSelectedCategories([]);
    };

    // Handle export
    const handleExport = () => {
        setExporting(true);
        const queryString = buildQueryString();
        const exportUrl = `/export/${format}/?${queryString}`;

        // Create a temporary link to trigger download
        const link = document.createElement('a');
        link.href = exportUrl;
        link.download = `${filename}.${format}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        // Show success state
        setTimeout(() => {
            setExporting(false);
            setExportSuccess(true);
            setTimeout(() => {
                setExportSuccess(false);
                setStep(1);
            }, 2000);
        }, 1000);
    };

    // Reset modal
    const resetModal = () => {
        setStep(1);
        setFormat('csv');
        setDateFrom('');
        setDateTo('');
        setSelectedCategories([]);
        setFilename('volunteer_opportunities');
        setPreviewData([]);
        setExportSuccess(false);
    };

    // Step Indicator Component
    const StepIndicator = () => (
        <div className="step-indicator">
            <div className={`step ${step >= 1 ? (step > 1 ? 'completed' : 'active') : ''}`}>
                <span className="step-number">{step > 1 ? <i className="bi bi-check"></i> : '1'}</span>
                <span className="step-label">Configure</span>
            </div>
            <div className="step-connector"></div>
            <div className={`step ${step >= 2 ? (step > 2 ? 'completed' : 'active') : ''}`}>
                <span className="step-number">{step > 2 ? <i className="bi bi-check"></i> : '2'}</span>
                <span className="step-label">Preview</span>
            </div>
            <div className="step-connector"></div>
            <div className={`step ${step >= 3 ? 'active' : ''}`}>
                <span className="step-number">3</span>
                <span className="step-label">Export</span>
            </div>
        </div>
    );

    // Step 1: Configuration
    const renderStep1 = () => (
        <div>
            {/* Export Format */}
            <div className="mb-4">
                <label className="form-label fw-bold">
                    <i className="bi bi-file-earmark me-1"></i>Export Format
                </label>
                <div className="d-flex gap-3 flex-wrap">
                    <button
                        type="button"
                        className={`export-format-btn csv ${format === 'csv' ? 'active' : ''}`}
                        onClick={() => setFormat('csv')}
                    >
                        <i className="bi bi-filetype-csv"></i>
                        <strong>CSV</strong>
                        <small className="text-muted d-block">Spreadsheet</small>
                    </button>
                    <button
                        type="button"
                        className={`export-format-btn json ${format === 'json' ? 'active' : ''}`}
                        onClick={() => setFormat('json')}
                    >
                        <i className="bi bi-filetype-json"></i>
                        <strong>JSON</strong>
                        <small className="text-muted d-block">Data Format</small>
                    </button>
                    <button
                        type="button"
                        className={`export-format-btn pdf ${format === 'pdf' ? 'active' : ''}`}
                        onClick={() => setFormat('pdf')}
                    >
                        <i className="bi bi-filetype-pdf"></i>
                        <strong>PDF</strong>
                        <small className="text-muted d-block">Document</small>
                    </button>
                </div>
            </div>

            {/* Date Range Filter */}
            <div className="filter-section">
                <label className="form-label fw-bold">
                    <i className="bi bi-calendar-range me-1"></i>Date Range (Optional)
                </label>
                <div className="row g-3">
                    <div className="col-md-6">
                        <label className="form-label text-muted small">From</label>
                        <input
                            type="date"
                            className="form-control"
                            value={dateFrom}
                            onChange={(e) => setDateFrom(e.target.value)}
                        />
                    </div>
                    <div className="col-md-6">
                        <label className="form-label text-muted small">To</label>
                        <input
                            type="date"
                            className="form-control"
                            value={dateTo}
                            onChange={(e) => setDateTo(e.target.value)}
                        />
                    </div>
                </div>
            </div>

            {/* Category Filter */}
            <div className="filter-section">
                <div className="d-flex justify-content-between align-items-center mb-2">
                    <label className="form-label fw-bold mb-0">
                        <i className="bi bi-tags me-1"></i>Categories (Optional)
                    </label>
                    <div>
                        <button type="button" className="btn btn-link btn-sm p-0 me-2" onClick={selectAllCategories}>
                            Select All
                        </button>
                        <button type="button" className="btn btn-link btn-sm p-0 text-muted" onClick={clearAllCategories}>
                            Clear
                        </button>
                    </div>
                </div>
                <div className="d-flex flex-wrap">
                    {categories.map(category => (
                        <label key={category.id} className="category-checkbox">
                            <input
                                type="checkbox"
                                className="form-check-input me-1"
                                checked={selectedCategories.includes(category.id.toString())}
                                onChange={() => toggleCategory(category.id.toString())}
                            />
                            <span>{category.name}</span>
                            <span className="text-muted ms-1">({category.opportunity_count})</span>
                        </label>
                    ))}
                    {categories.length === 0 && (
                        <p className="text-muted mb-0">No categories available</p>
                    )}
                </div>
                <small className="text-muted">Leave empty to export all categories</small>
            </div>

            {/* Custom Filename */}
            <div className="mb-4">
                <label className="form-label fw-bold">
                    <i className="bi bi-pencil me-1"></i>Filename
                </label>
                <div className="input-group">
                    <input
                        type="text"
                        className="form-control"
                        value={filename}
                        onChange={(e) => setFilename(e.target.value.replace(/[^a-zA-Z0-9_-]/g, '_'))}
                        placeholder="Enter filename"
                    />
                    <span className="input-group-text">.{format}</span>
                </div>
            </div>

            {/* Actions */}
            <div className="d-flex justify-content-end gap-2">
                <button type="button" className="btn btn-outline-secondary" data-bs-dismiss="modal">
                    Cancel
                </button>
                <button type="button" className="btn btn-primary" onClick={() => setStep(2)}>
                    Preview Data <i className="bi bi-arrow-right ms-1"></i>
                </button>
            </div>
        </div>
    );

    // Step 2: Preview
    const renderStep2 = () => (
        <div style={{ position: 'relative' }}>
            {previewLoading && (
                <div className="loading-overlay">
                    <div className="text-center">
                        <div className="spinner-border text-primary mb-2" role="status"></div>
                        <p className="mb-0">Loading preview...</p>
                    </div>
                </div>
            )}

            {/* Export Summary */}
            <div className="export-summary mb-4">
                <div className="row">
                    <div className="col-4">
                        <div className="summary-item">
                            <div className="summary-value">{totalCount}</div>
                            <div className="summary-label">Opportunities</div>
                        </div>
                    </div>
                    <div className="col-4">
                        <div className="summary-item">
                            <div className="summary-value">{totalVolunteers}</div>
                            <div className="summary-label">Total Volunteers</div>
                        </div>
                    </div>
                    <div className="col-4">
                        <div className="summary-item">
                            <div className="summary-value text-uppercase">{format}</div>
                            <div className="summary-label">Format</div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Active Filters */}
            <div className="mb-3">
                <small className="text-muted">
                    <strong>Active Filters:</strong>{' '}
                    {dateFrom && <span className="badge bg-primary me-1">From: {dateFrom}</span>}
                    {dateTo && <span className="badge bg-primary me-1">To: {dateTo}</span>}
                    {selectedCategories.length > 0 && (
                        <span className="badge bg-secondary me-1">
                            {selectedCategories.length} categories selected
                        </span>
                    )}
                    {!dateFrom && !dateTo && selectedCategories.length === 0 && (
                        <span className="badge bg-light text-dark">All data (no filters)</span>
                    )}
                </small>
            </div>

            {/* Preview Table */}
            <div className="preview-table border rounded mb-4">
                <table className="table table-striped table-hover mb-0">
                    <thead className="table-light sticky-top">
                        <tr>
                            <th>Title</th>
                            <th>Category</th>
                            <th>Date</th>
                            <th className="text-center">Volunteers</th>
                        </tr>
                    </thead>
                    <tbody>
                        {previewData.length > 0 ? (
                            previewData.map(opp => (
                                <tr key={opp.id}>
                                    <td>{opp.title}</td>
                                    <td><span className="badge bg-secondary">{opp.category}</span></td>
                                    <td>{opp.date}</td>
                                    <td className="text-center">{opp.volunteer_count}</td>
                                </tr>
                            ))
                        ) : (
                            <tr>
                                <td colSpan="4" className="text-center text-muted py-4">
                                    No opportunities match your filters
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>

            {/* Actions */}
            <div className="d-flex justify-content-between">
                <button type="button" className="btn btn-outline-secondary" onClick={() => setStep(1)}>
                    <i className="bi bi-arrow-left me-1"></i> Back
                </button>
                <button
                    type="button"
                    className="btn btn-primary"
                    onClick={() => setStep(3)}
                    disabled={previewData.length === 0}
                >
                    Continue <i className="bi bi-arrow-right ms-1"></i>
                </button>
            </div>
        </div>
    );

    // Step 3: Confirm & Export
    const renderStep3 = () => (
        <div className="text-center py-4">
            {exportSuccess ? (
                <div>
                    <div className="mb-4">
                        <i className="bi bi-check-circle-fill text-success" style={{ fontSize: '4rem' }}></i>
                    </div>
                    <h4 className="text-success">Export Successful!</h4>
                    <p className="text-muted">Your file has been downloaded.</p>
                </div>
            ) : exporting ? (
                <div>
                    <div className="spinner-border text-primary mb-4" style={{ width: '3rem', height: '3rem' }} role="status"></div>
                    <h4>Generating Export...</h4>
                    <p className="text-muted">Please wait while we prepare your file.</p>
                </div>
            ) : (
                <div>
                    <div className="mb-4">
                        <i className="bi bi-file-earmark-arrow-down text-primary" style={{ fontSize: '4rem' }}></i>
                    </div>
                    <h4>Ready to Export</h4>
                    <p className="text-muted mb-4">
                        You're about to download <strong>{totalCount} opportunities</strong> as a <strong>{format.toUpperCase()}</strong> file.
                    </p>
                    <div className="card bg-light mx-auto" style={{ maxWidth: '400px' }}>
                        <div className="card-body">
                            <div className="d-flex justify-content-between mb-2">
                                <span className="text-muted">Filename:</span>
                                <strong>{filename}.{format}</strong>
                            </div>
                            <div className="d-flex justify-content-between mb-2">
                                <span className="text-muted">Records:</span>
                                <strong>{totalCount}</strong>
                            </div>
                            <div className="d-flex justify-content-between">
                                <span className="text-muted">Total Volunteers:</span>
                                <strong>{totalVolunteers}</strong>
                            </div>
                        </div>
                    </div>
                    <div className="d-flex justify-content-center gap-2 mt-4">
                        <button type="button" className="btn btn-outline-secondary" onClick={() => setStep(2)}>
                            <i className="bi bi-arrow-left me-1"></i> Back
                        </button>
                        <button type="button" className="btn btn-success btn-lg" onClick={handleExport}>
                            <i className="bi bi-download me-1"></i> Download Now
                        </button>
                    </div>
                </div>
            )}
        </div>
    );

    return (
        <div>
            <StepIndicator />
            {step === 1 && renderStep1()}
            {step === 2 && renderStep2()}
            {step === 3 && renderStep3()}
        </div>
    );
}

// Initialize export modal when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    const exportModal = document.getElementById('exportModal');
    if (exportModal) {
        exportModal.addEventListener('show.bs.modal', function () {
            const container = document.getElementById('exportModalContent');
            const root = ReactDOM.createRoot(container);
            root.render(<ExportModal />);
        });
    }
});