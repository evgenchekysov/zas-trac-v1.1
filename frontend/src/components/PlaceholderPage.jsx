export default function PlaceholderPage({ title }) {
  return (
    <div className="h-full flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-2xl font-semibold text-slate-600 mb-4">
          {title}
        </h1>

        <div className="text-slate-400">
          Страница в разработке
        </div>
      </div>
    </div>
  );
}