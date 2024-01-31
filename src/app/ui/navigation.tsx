'use client';
import NavLinks from '@/app/ui/nav-links';
import { useState } from 'react';


export default function Navigation() {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <header className="p-5 bg-black text-white flex flex-col md:flex-row justify-between items-center border-b border-gray-300">
        <div className="flex justify-between items-center w-full md:w-auto">
            <h1 className="mb-4 md:mb-0 align-middle">&gt; BYTE.UY<span className='blink'>|</span></h1>
            <button className="md:hidden" onClick={() => setIsOpen(!isOpen)}>
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" className="h-6 w-6">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
            </button>
        </div>
        <nav className={`mb-4 md:mb-0 ${isOpen ? 'block' : 'hidden'} md:block`}>
            <ul className="flex flex-col md:flex-row space-y-2 md:space-y-0 md:space-x-4">
                <NavLinks />
            </ul>
        </nav>
        <div className={`relative ${isOpen ? 'block' : 'hidden'} md:block`}>
            <input type="text" placeholder="Buscar..." className="p-2 pl-10 bg-black text-white border border-gray-300" />
            <span className="absolute left-2 top-2">🔍</span>
        </div>
        </header>
    );
}