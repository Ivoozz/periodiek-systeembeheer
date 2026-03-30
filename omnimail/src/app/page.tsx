import React from 'react';
import { Mail, Send, File, Trash2, Settings, Archive, RefreshCw, User, Plus, Search, Star, MoreVertical } from 'lucide-react';

export default function Home() {
  return (
    <div className="flex h-screen bg-zinc-50 text-zinc-900 overflow-hidden font-sans">
      {/* Sidebar */}
      <aside className="w-64 bg-zinc-900 text-zinc-300 flex flex-col border-r border-zinc-800">
        <div className="p-4 flex items-center gap-3 text-white border-b border-zinc-800">
          <Mail className="w-6 h-6 text-indigo-400" />
          <h1 className="font-bold text-lg tracking-wide">OmniMail</h1>
        </div>

        {/* Account Switcher / Add Account */}
        <div className="p-4 border-b border-zinc-800">
          <div className="flex items-center justify-between group cursor-pointer hover:bg-zinc-800 p-2 rounded-md transition-colors">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-indigo-500 flex items-center justify-center text-white font-bold text-sm">
                JD
              </div>
              <div className="text-sm">
                <p className="font-medium text-white">john@doe.com</p>
                <p className="text-xs text-zinc-500">iCloud Mail</p>
              </div>
            </div>
            <MoreVertical className="w-4 h-4 text-zinc-500" />
          </div>
          <button className="mt-2 w-full flex items-center justify-center gap-2 text-xs py-2 border border-zinc-700 rounded hover:bg-zinc-800 transition-colors">
            <Plus className="w-4 h-4" /> Add Account (M365, Gmail)
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto py-4">
          <ul className="space-y-1 px-2">
            {[
              { icon: Mail, label: 'Inbox', badge: '12' },
              { icon: Star, label: 'Starred' },
              { icon: Send, label: 'Sent' },
              { icon: File, label: 'Drafts', badge: '3' },
              { icon: Archive, label: 'Archive' },
              { icon: Trash2, label: 'Trash' },
            ].map((item, idx) => (
              <li key={idx}>
                <a
                  href="#"
                  className={`flex items-center justify-between px-3 py-2 rounded-md transition-colors ${
                    item.label === 'Inbox' ? 'bg-indigo-600/10 text-indigo-400' : 'hover:bg-zinc-800 hover:text-white'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <item.icon className="w-4 h-4" />
                    <span className="text-sm font-medium">{item.label}</span>
                  </div>
                  {item.badge && (
                    <span className="text-xs bg-zinc-800 px-2 py-0.5 rounded-full">{item.badge}</span>
                  )}
                </a>
              </li>
            ))}
          </ul>
        </nav>

        <div className="p-4 border-t border-zinc-800">
          <a href="#" className="flex items-center gap-3 px-3 py-2 rounded-md hover:bg-zinc-800 hover:text-white transition-colors">
            <Settings className="w-4 h-4" />
            <span className="text-sm font-medium">Settings</span>
          </a>
        </div>
      </aside>

      {/* Main Mail List */}
      <main className="w-96 flex flex-col border-r border-zinc-200 bg-white">
        <div className="p-4 border-b border-zinc-200 flex items-center justify-between">
          <h2 className="font-semibold text-lg">Inbox</h2>
          <button className="p-1 hover:bg-zinc-100 rounded text-zinc-500">
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
        <div className="p-3 border-b border-zinc-200">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-zinc-400" />
            <input
              type="text"
              placeholder="Search emails..."
              className="w-full pl-9 pr-3 py-2 bg-zinc-100 border-none rounded-md text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
            />
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto">
          {[
            { sender: 'Microsoft 365', subject: 'Your weekly insights', preview: 'Here are your insights for the past week...', time: '10:42 AM', unread: true },
            { sender: 'GitHub', subject: '[OmniMail] New issue assigned', preview: 'You have been assigned to issue #42 in the OmniMail repository...', time: 'Yesterday', unread: false },
            { sender: 'Apple', subject: 'Your iCloud storage is almost full', preview: 'Upgrade your iCloud storage today to keep backing up your devices.', time: 'Mar 9', unread: true },
            { sender: 'Google', subject: 'Security alert for your linked Google Account', preview: 'We noticed a new sign-in to your Google Account from a Debian LXC device.', time: 'Mar 8', unread: false },
          ].map((mail, idx) => (
            <div
              key={idx}
              className={`p-4 border-b border-zinc-100 cursor-pointer transition-colors ${
                mail.unread ? 'bg-white' : 'bg-zinc-50 text-zinc-600'
              } hover:bg-indigo-50`}
            >
              <div className="flex justify-between items-baseline mb-1">
                <span className={`text-sm ${mail.unread ? 'font-semibold text-zinc-900' : 'font-medium'}`}>{mail.sender}</span>
                <span className="text-xs text-zinc-500">{mail.time}</span>
              </div>
              <h3 className={`text-sm mb-1 truncate ${mail.unread ? 'font-semibold text-zinc-800' : ''}`}>{mail.subject}</h3>
              <p className="text-xs text-zinc-500 truncate">{mail.preview}</p>
            </div>
          ))}
        </div>
      </main>

      {/* Detail View */}
      <section className="flex-1 bg-white flex flex-col">
        <header className="p-6 border-b border-zinc-200 flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-zinc-900 mb-2">Your weekly insights</h1>
            <div className="flex items-center gap-2 text-sm text-zinc-500">
              <span className="font-medium text-zinc-900">Microsoft 365</span>
              <span>&lt;no-reply@microsoft.com&gt;</span>
              <span>to me</span>
            </div>
          </div>
          <div className="flex gap-2">
            <button className="p-2 hover:bg-zinc-100 rounded-md text-zinc-600 transition-colors"><Star className="w-5 h-5" /></button>
            <button className="p-2 hover:bg-zinc-100 rounded-md text-zinc-600 transition-colors"><Trash2 className="w-5 h-5" /></button>
          </div>
        </header>
        
        <div className="p-8 flex-1 overflow-y-auto text-zinc-800 leading-relaxed max-w-3xl">
          <p className="mb-4">Hello John,</p>
          <p className="mb-4">Here are your weekly insights across your Microsoft 365 apps. You've had a productive week!</p>
          <div className="p-6 bg-zinc-50 rounded-lg border border-zinc-200 mb-4 text-center">
            <h3 className="text-lg font-semibold mb-2">14 Meetings Attended</h3>
            <p className="text-sm text-zinc-500">That's 2 more than last week.</p>
          </div>
          <p className="mb-4">Log in to your dashboard to see more detailed analytics.</p>
          <p>Best,<br/>The M365 Team</p>
        </div>

        <div className="p-4 border-t border-zinc-200">
          <div className="relative">
            <textarea 
              className="w-full p-4 border border-zinc-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none resize-none"
              placeholder="Reply to Microsoft 365..."
              rows={3}
            ></textarea>
            <button className="absolute bottom-6 right-6 bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-700 transition-colors">
              Send
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
