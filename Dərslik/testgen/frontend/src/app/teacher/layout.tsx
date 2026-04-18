import TeacherSidebar from '@/components/TeacherSidebar'
import TeacherMobileBar from '@/components/TeacherMobileBar'
import RequireRole from '@/components/RequireRole'

export default function TeacherLayout({ children }: { children: React.ReactNode }) {
  return (
    <RequireRole role="teacher">
      <div className="flex min-h-screen">
        <TeacherSidebar />
        <div className="flex-1 min-w-0 flex flex-col">
          <TeacherMobileBar />
          <div className="flex-1">{children}</div>
        </div>
      </div>
    </RequireRole>
  )
}
