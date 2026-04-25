import {
  ClientSideRowModelApiModule,
  ClientSideRowModelModule,
  ColumnApiModule,
  CsvExportModule,
  CustomFilterModule,
  DateFilterModule,
  EventApiModule,
  GridStateModule,
  LocaleModule,
  ModuleRegistry,
  NumberFilterModule,
  PaginationModule,
  QuickFilterModule,
  RenderApiModule,
  RowAutoHeightModule,
  RowSelectionModule,
  TextFilterModule,
  ValidationModule,
} from 'ag-grid-community';

let registered = false;

export function ensureAgGridModulesRegistered() {
  if (registered) return;

  ModuleRegistry.registerModules([
    ClientSideRowModelModule,
    ClientSideRowModelApiModule,
    ColumnApiModule,
    CsvExportModule,
    CustomFilterModule,
    DateFilterModule,
    EventApiModule,
    GridStateModule,
    LocaleModule,
    NumberFilterModule,
    PaginationModule,
    QuickFilterModule,
    RenderApiModule,
    RowAutoHeightModule,
    RowSelectionModule,
    TextFilterModule,
    ValidationModule,
  ]);

  registered = true;
}
