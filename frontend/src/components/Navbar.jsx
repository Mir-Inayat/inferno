import React from "react";
import { Link } from "react-router-dom";
function Navbar() {
    return (
        <nav className="navbar">
            <div className="navbar-brand">
                <h2>SmartDocMate</h2>
            </div>
            <ul className="navbar-links">
                <li>
                    <Link to="/" className={location.pathname === "/" ? "active" : ""}>
                        Home
                    </Link>
                </li>
                <li>
                    <Link to="/dashboard" className={location.pathname === "/dashboard" ? "active" : ""}>
                        Dashboard
                    </Link>
                </li>
            </ul>
        </nav>
    );
};

export default Navbar;