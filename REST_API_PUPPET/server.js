const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3005;
const JWT_SECRET = 'your-super-secret-jwt-key-change-this-in-production';

// Middleware
app.use(express.json());
app.use(cors());

// Sample data
const users = [
  {
    id: 1,
    username: 'admin',
    password: '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', // password
    role: 'admin'
  },
  {
    id: 2,
    username: 'user',
    password: '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', // password
    role: 'user'
  }
];

const products = [
  { id: 1, name: 'Laptop', category: 'electronics', price: 999, brand: 'TechCorp', inStock: true },
  { id: 2, name: 'Phone', category: 'electronics', price: 599, brand: 'MobileTech', inStock: true },
  { id: 3, name: 'Desk', category: 'furniture', price: 299, brand: 'FurnitureCo', inStock: false },
  { id: 4, name: 'Chair', category: 'furniture', price: 149, brand: 'ComfortSeats', inStock: true },
  { id: 5, name: 'Headphones', category: 'electronics', price: 199, brand: 'AudioMax', inStock: true },
  { id: 6, name: 'Bookshelf', category: 'furniture', price: 89, brand: 'WoodWorks', inStock: true }
];

// Authentication middleware
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }

  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) {
      return res.status(403).json({ error: 'Invalid or expired token' });
    }
    req.user = user;
    next();
  });
};

// ROUTE 1: Public route - Get all products (no authentication required)
app.get('/api/products', (req, res) => {
  res.json({
    success: true,
    data: products,
    message: 'Products retrieved successfully'
  });
});

// Login route to get JWT token
app.post('/api/login', async (req, res) => {
  const { username, password } = req.body;

  if (!username || !password) {
    return res.status(400).json({ error: 'Username and password required' });
  }

  const user = users.find(u => u.username === username);
  if (!user) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }

  const validPassword = await bcrypt.compare(password, user.password);
  if (!validPassword) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }

  const token = jwt.sign(
    { id: user.id, username: user.username, role: user.role },
    JWT_SECRET,
    { expiresIn: '1h' }
  );

  res.json({
    success: true,
    token,
    user: { id: user.id, username: user.username, role: user.role }
  });
});

// ROUTE 2: Protected route - Get user profile (requires authentication)
app.get('/api/profile', authenticateToken, (req, res) => {
  const user = users.find(u => u.id === req.user.id);
  if (!user) {
    return res.status(404).json({ error: 'User not found' });
  }

  res.json({
    success: true,
    data: {
      id: user.id,
      username: user.username,
      role: user.role,
      lastLogin: new Date().toISOString()
    },
    message: 'Profile retrieved successfully'
  });
});

// ROUTE 3: POST route with dynamic filtering
app.post('/api/products/search', (req, res) => {
  const { filters = {}, sort = {}, pagination = {} } = req.body;
  
  let filteredProducts = [...products];

  // Apply filters dynamically
  Object.keys(filters).forEach(key => {
    const filterValue = filters[key];
    
    if (filterValue !== undefined && filterValue !== null && filterValue !== '') {
      filteredProducts = filteredProducts.filter(product => {
        const productValue = product[key];
        
        // Handle different filter types
        if (typeof filterValue === 'string') {
          return productValue && productValue.toString().toLowerCase().includes(filterValue.toLowerCase());
        } else if (typeof filterValue === 'number') {
          return productValue=== filterValue;
        } else if (typeof filterValue === 'boolean') {
          return productValue === filterValue;
        } else if (typeof filterValue === 'object') {
          // Handle range filters like { min: 100, max: 500 }
          if (filterValue.min !== undefined && productValue < filterValue.min) {
            return false;
          }
          if (filterValue.max !== undefined && productValue > filterValue.max) {
            return false;
          }
          return true;
        }
        return true;
      });
    }
  });

  // Apply sorting
  if (sort.field && sort.order) {
    filteredProducts.sort((a, b) => {
      const aVal = a[sort.field];
      const bVal = b[sort.field];
      
      if (sort.order === 'asc') {
        return aVal > bVal ? 1 : -1;
      } else {
        return aVal < bVal ? 1 : -1;
      }
    });
  }

  // Apply pagination
  const page = pagination.page || 1;
  const limit = pagination.limit || 10;
  const startIndex = (page - 1) * limit;
  const endIndex = startIndex + limit;
  
  const paginatedProducts = filteredProducts.slice(startIndex, endIndex);

  res.json({
    success: true,
    data: paginatedProducts,
    pagination: {
      currentPage: page,
      totalPages: Math.ceil(filteredProducts.length / limit),
      totalItems: filteredProducts.length,
      itemsPerPage: limit
    },
    message: 'Products filtered successfully'
  });
});

// Health check route
app.get('/api/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
  console.log('\n=== API Routes ===');
  console.log('GET  /api/products       - Get all products (public)');
  console.log('POST /api/login          - Login to get JWT token');
  console.log('GET  /api/profile        - Get user profile (protected)');
  console.log('POST /api/products/search - Search products with filters');
  console.log('GET  /api/health         - Health check');
});

module.exports = app; 
